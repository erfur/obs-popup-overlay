# speech recognition project

Currently unnamed. The aim is to catch phrases like "arch" in real time and pop
animations on the screen for sum fun. Here are some projects of interest:

- https://github.com/Uberi/speech_recognition
- https://github.com/yf-dev/OpenCaptionsOverlay
- https://webcaptioner.com/captioner

## speech_recognition

I prefer using an offline api for some privacy. This project supports three:

- https://cmusphinx.github.io/wiki/
- https://github.com/alphacep/vosk-api/
- https://github.com/seasalt-ai/snowboy (deprecated)

snowboy is trained for predetermined words (only about ten words), so its not
really an option for me.

## vosk api

By default vosk api works well, especially with the biggest model available
(`vosk-model-en-us-0.22.zip`, taking ~2GB disk space), though currently its not
possible to define a grammar for specific words. The native interface does
support this, so it was as trivial as adding a couple lines to the python code
[[1]].

[1]: ./init.patch

However, after adding and supplying a grammar, an error message is logged:

```
"Runtime graphs are not supported by this model"
```

This occurs when the used model does not have a `HCLr.fst` file available. This
is the case for the big model but the small model
`vosk-model-en-us-0.22-lgraph.zip` does have this file so I switched to this
model. Now I can use the model to only recognize the `archlinux` phrase.

[2]: https://alphacephei.com/vosk/models