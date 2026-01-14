import numpy as np
import torch
import torchaudio

# HACK: see https://github.com/speechbrain/speechbrain/issues/3012
if not hasattr(torchaudio, "list_audio_backends"):
    torchaudio.list_audio_backends = lambda: [""]  # type: ignore

from ovos_config.locale import get_valid_languages
from ovos_plugin_manager.templates.transformers import AudioLanguageDetector
from ovos_plugin_manager.utils.audio import AudioData, AudioFile
from ovos_utils.xdg_utils import xdg_data_home
from speechbrain.inference import EncoderClassifier


class SpeechBrainLangClassifier(AudioLanguageDetector):
    def __init__(self, config=None):
        """
        Initialize the SpeechBrain language classifier plugin instance.
        
        Parameters:
            config (dict, optional): Configuration dictionary. Recognized keys:
                - "model" (str): SpeechBrain model identifier or path to use (defaults to
                  "speechbrain/lang-id-commonlanguage_ecapa").
                - "use_cuda" (bool): If true, attempt to load the model onto CUDA; otherwise
                  load on the default device.
        
        Side effects:
            Sets up the plugin via the superclass and initializes `self.engine` with a
            SpeechBrain EncoderClassifier instance.
        """
        config = config or {}
        super().__init__("ovos-audio-transformer-plugin-speechbrain-langdetect", 10, config)
        model = self.config.get("model") or "speechbrain/lang-id-commonlanguage_ecapa"
        if self.config.get("use_cuda"):
            self.engine = EncoderClassifier.from_hparams(source=model, savedir=f"{xdg_data_home()}/speechbrain",
                                                         run_opts={"device": "cuda"})
        else:
            self.engine = EncoderClassifier.from_hparams(source=model, savedir=f"{xdg_data_home()}/speechbrain")

    def signal2probs(self, signal):
        """
        Map a model input signal to language probability scores.
        
        Runs the classifier on the provided preprocessed audio signal and returns a mapping from lowercase language codes to their predicted probabilities.
        
        Parameters:
            signal: Model-ready audio input (batch tensor or structure accepted by the classifier's classify_batch).
        
        Returns:
            dict: Mapping where each key is a lowercase BCP-47-like language code (e.g., "en-us") and each value is the language probability as a float between 0 and 1.
        """
        probs, _, _, _ = self.engine.classify_batch(signal)
        probs = torch.softmax(probs[0], dim=0)
        labels = self.engine.hparams.label_encoder.decode_ndim(range(len(probs)))
        results = {}
        for prob, label in sorted(zip(probs, labels), reverse=True):
            results[label.split(":")[0]] = prob.item()

        # the labels are the language name in english, map to lang-codes
        langmap = {'Arabic': 'ar-SA',
                   'Basque': 'eu-ES',
                   'Breton': 'br-FR',
                   'Catalan': 'ca-ES',
                   'Chinese_China': 'zh-CN',
                   'Chinese_Hongkong': 'zh-HK',
                   'Chinese_Taiwan': 'zh-TW',
                   'Chuvash': 'cv-RU',
                   'Czech': 'cs-CZ',
                   'Dhivehi': 'dv-MV',
                   'Dutch': 'nl-NL',
                   'English': 'en-US',
                   'Esperanto': 'eo',
                   'Estonian': 'et-EE',
                   'French': 'fr-FR',
                   'Frisian': 'fy-NL',
                   'Georgian': 'ka-GE',
                   'German': 'de-DE',
                   'Greek': 'el-GR',
                   'Hakha_Chin': 'cnh',
                   'Indonesian': 'id-ID',
                   'Interlingua': 'ia',
                   'Italian': 'it-IT',
                   'Japanese': 'ja-JP',
                   'Kabyle': 'kab-DZ',
                   'Kinyarwanda': 'rw-RW',
                   'Kyrgyz': 'ky-KG',
                   'Latvian': 'lv-LV',
                   'Maltese': 'mt-MT',
                   'Mongolian': 'mn-MN',
                   'Persian': 'fa-IR',
                   'Polish': 'pl-PL',
                   'Portuguese': 'pt-PT',
                   'Romanian': 'ro-RO',
                   'Romansh_Sursilvan': 'rm-Sursilvan',
                   'Russian': 'ru-RU',
                   'Sakha': 'sah-RU',
                   'Slovenian': 'sl-SI',
                   'Spanish': 'es-ES',
                   'Swedish': 'sv-SE',
                   'Tamil': 'ta-IN',
                   'Tatar': 'tt-RU',
                   'Turkish': 'tr-TR',
                   'Ukrainian': 'uk-UA',
                   'Welsh': 'cy-GB'}

        return {langmap[k].lower(): v for k, v in results.items()}

    # plugin api
    def detect(self, audio_data: bytes, valid_langs=None):
        """
        Detects the most likely language for the given audio and returns the language code with its probability.
        
        Parameters:
            audio_data (bytes | AudioData): Raw audio bytes or an AudioData instance; raw bytes will be wrapped into an AudioData with 16 kHz sample rate and 2 channels.
            valid_langs (Iterable[str], optional): Iterable of allowed BCP-47-like language codes to consider (e.g., "en-US", "es-ES"); if omitted the global get_valid_languages() set is used.
        
        Returns:
            tuple: If only one language is in `valid_langs`, returns (audio_data, {}) indicating no classification was performed. Otherwise returns `(lang_code, probability)` where `lang_code` is the selected language code (string) and `probability` is the normalized confidence as a float between 0 and 1.
        """
        if not isinstance(audio_data, AudioData):
            audio_data = AudioData(audio_data, 16000, 2)

        signal = torch.from_numpy(audio_data.get_np_float32()).float()
        valid = valid_langs or get_valid_languages()
        if len(valid) == 1:
            # no classification needed
            return audio_data, {}

        probs = self.signal2probs(signal)
        valid2 = [l.split("-")[0] for l in valid]
        probs = [(k, v) for k, v in probs.items()
                 if k.split("-")[0] in valid2]
        total = sum(p[1] for p in probs) or 1
        probs = [(k, v / total) for k, v in probs]

        lang, prob = max(probs, key=lambda k: k[1])
        return lang, prob


if __name__ == "__main__":
    jfk = "/home/miro/PycharmProjects/ovos-stt-plugin-fasterwhisper/jfk.wav"
    with AudioFile(jfk) as source:
        audio = source.read()

    s = SpeechBrainLangClassifier()
    lang, prob = s.detect(audio.get_wav_data(), valid_langs=["en-us", "es-es"])
    print(lang, prob)
    # en-us 0.5979952496320518