let currentAudio = null;

window.addEventListener("message", async (event) => {
  if (event.data.type === "tts-generate") {
    try {
      if (!tts) {
        console.error("TTS_HELPER Generate: System not initialized");
        throw new Error("TTS_HELPER system not yet initialized");
      }

      if (currentAudio) {
        console.log("TTS_HELPER Generate: Stopping previous audio");
        currentAudio.pause();
        URL.revokeObjectURL(currentAudio.src);
        currentAudio.remove();
        currentAudio = null;
      }

      console.log("TTS_HELPER Generate: Generating new audio", event.data);

      const audio = tts.generate(event.data);

      await createAudioTag(audio);
      console.log("TTS_HELPER Generate: Audio generation complete");

      window.parent.postMessage({ type: "tts-complete" }, "*");
    } catch (error) {
      console.error("TTS_HELPER Generate: Error occurred", error);
      window.parent.postMessage(
        {
          type: "tts-error",
          error: error.message,
        },
        "*"
      );
    }
  }
});

Module = {};
Module.onRuntimeInitialized = function () {
  console.log("TTS_HELPER Init: Model files downloaded");
  console.log("TTS_HELPER Init: Initializing system");
  tts = createOfflineTts(Module);

  window.parent.postMessage({ type: "tts-ready" }, "*");
  console.log("TTS_HELPER Init: System ready");
};

async function createAudioTag(generateAudio) {
  console.log("TTS_HELPER Audio: Creating new audio element");
  const blob = toWav(generateAudio.samples, generateAudio.sampleRate);
  const audioURL = URL.createObjectURL(blob);

  const audio = document.createElement("audio");
  audio.src = audioURL;
  audio.style.display = "none";

  currentAudio = audio;
  document.body.appendChild(audio);

  try {
    console.log("TTS_HELPER Audio: Attempting autoplay");
    await audio.play();
  } catch (err) {
    console.log("TTS_HELPER Audio: Autoplay failed, waiting for user interaction");
    const resumeAudio = async () => {
      if (audio === currentAudio) {
        console.log("TTS_HELPER Audio: User initiated playback");
        await audio.play();
      } else {
        console.log("TTS_HELPER Audio: Playback cancelled - newer audio exists");
      }
      document.removeEventListener("click", resumeAudio);
    };

    document.addEventListener("click", resumeAudio, { once: true });
    console.log("TTS_HELPER Audio: Click handler attached");
  }

  audio.onended = () => {
    console.log("TTS_HELPER Audio: Playback ended, cleaning up");
    if (audio === currentAudio) {
      currentAudio = null;
    }
    URL.revokeObjectURL(audioURL);
    audio.remove();
  };
}

// this function is copied/modified from
// https://gist.github.com/meziantou/edb7217fddfbb70e899e
function toWav(floatSamples, sampleRate) {
  let samples = new Int16Array(floatSamples.length);
  for (let i = 0; i < samples.length; ++i) {
    let s = floatSamples[i];
    if (s >= 1) s = 1;
    else if (s <= -1) s = -1;

    samples[i] = s * 32767;
  }

  let buf = new ArrayBuffer(44 + samples.length * 2);
  var view = new DataView(buf);

  // http://soundfile.sapp.org/doc/WaveFormat/
  //                   F F I R
  view.setUint32(0, 0x46464952, true); // chunkID
  view.setUint32(4, 36 + samples.length * 2, true); // chunkSize
  //                   E V A W
  view.setUint32(8, 0x45564157, true); // format
  //
  //                      t m f
  view.setUint32(12, 0x20746d66, true); // subchunk1ID
  view.setUint32(16, 16, true); // subchunk1Size, 16 for PCM
  view.setUint32(20, 1, true); // audioFormat, 1 for PCM
  view.setUint16(22, 1, true); // numChannels: 1 channel
  view.setUint32(24, sampleRate, true); // sampleRate
  view.setUint32(28, sampleRate * 2, true); // byteRate
  view.setUint16(32, 2, true); // blockAlign
  view.setUint16(34, 16, true); // bitsPerSample
  view.setUint32(36, 0x61746164, true); // Subchunk2ID
  view.setUint32(40, samples.length * 2, true); // subchunk2Size

  let offset = 44;
  for (let i = 0; i < samples.length; ++i) {
    view.setInt16(offset, samples[i], true);
    offset += 2;
  }

  return new Blob([view], { type: "audio/wav" });
}
