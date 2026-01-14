# SpeechBrain Lang detect

spoken language detector for ovos

models:
- [speechbrain/lang-id-commonlanguage_ecapa](https://huggingface.co/speechbrain/lang-id-commonlanguage_ecapa) - 45 langs
- [speechbrain/lang-id-voxlingua107-ecapa](https://huggingface.co/speechbrain/lang-id-voxlingua107-ecapa) - 107 langs
- [TalTechNLP/voxlingua107-epaca-tdnn](https://huggingface.co/TalTechNLP/voxlingua107-epaca-tdnn) - 107 langs
- [TalTechNLP/voxlingua107-epaca-tdnn-ce](https://huggingface.co/TalTechNLP/voxlingua107-epaca-tdnn-ce) - 107 langs
- [sahita/lang-VoxLingua107-ecapa](https://huggingface.co/sahita/lang-VoxLingua107-ecapa) - ( English, Hindi)
- [sahita/language-identification](https://huggingface.co/sahita/language-identification) - ( English, Hindi, Other)

```javascript
"listener": {
    "audio_transformers": {
        "ovos-audio-transformer-plugin-speechbrain-langdetect": {
            "model": "speechbrain/lang-id-langdetect-ecapa"
        }
    }
}
```