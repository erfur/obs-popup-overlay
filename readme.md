# obs-overlay-popup

<!-- todo
- explain voice_recognition callback
- explain frontend
- add requirements
- add how to use
- add downlader script
-->

Very primitive implementation of a popup plugin for obs. Catches given hotwords
through speech recognition and triggers the given image on the screen for sum
fun. The main purpose of this project is not to require an internet connection
for speech recognition. Because of this, an experimental approach is used.

## Web Interface

The web interface is provided with flask. Comms with the frontend is done
through websockets.

## Speech Recognition

There is a speech recognition module for python that supports multiple
APIs called [speech_recognition]. Among the APIs that are supported, three of
them can be used locally:

- https://cmusphinx.github.io/wiki/
- https://github.com/alphacep/vosk-api/
- https://github.com/seasalt-ai/snowboy (API deprecated)

Snowboy is trained for predetermined words (pretrained only for about ten
words), so its not really an option for this project. Sphinx requires a ton of
compilation (or a wheel download, which is not available for recents version of
python). That lead to Voks being the API that is used.

There are other projects like [OpenCaptionsOverlay], a captions overlay which
requires a twitch account setup and [webcaptioner.com], an online API mainly for
captions. These can be used to catch words; however for reasons given, they are
out of the scope of this project.

[speech_recognition]: https://github.com/Uberi/speech_recognition
[OpenCaptionsOverlay]: https://github.com/yf-dev/OpenCaptionsOverlay
[webcaptioner.com]: https://webcaptioner.com/captioner

### Vosk API

By default vosk api works well, especially with the biggest model available
(`vosk-model-en-us-0.22.zip`, taking ~2GB disk space), though currently its not
possible to define a grammar for specific words. The native interface does
support this, so it was as trivial as adding a couple lines to the python code
[init-patch].

[init-patch]: ./init.patch

However, after adding and supplying a grammar, an error message is logged:

```
"Runtime graphs are not supported by this model"
```

This occurs when the used model does not have a `HCLr.fst` file available. This
is the case for the big model but the small model
`vosk-model-en-us-0.22-lgraph.zip` does have this file so I switched to this
model. Now I can use the model to only recognize the `archlinux` phrase.

[2]: https://alphacephei.com/vosk/models