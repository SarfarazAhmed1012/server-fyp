const path = require("path");
const fs = require("fs");
const express = require("express");
const multer = require("multer");
const cors = require("cors");
const app = express();
const { spawn } = require("child_process");
const { request } = require("http");
const { response } = require("express");
const { stderr } = require("process");

app.use(cors());
app.use(express.static("uploads"));
app.use(express.json());
app.use(express.static("videoUpload"));
app.use(express.static("uploaded_audio"));

//-------------------------------------------------------------------------------//
// uploading video files
const tempVideoStorage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, "E:/toil/FYP/client/src/denoised-video/");
  },
  filename: function (req, file, cb) {
    const fileNameArr = file.originalname.split(".");
    // file name
    cb(null, `input_video.mp4`);
  },
});

var videoStorage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, "tmp/");
  },
  filename: (req, file, cb) => {
    const fileNameArr = file.originalname.split(".");
    // file name
    cb(null, `video.mp4`);
  },
});

const tempVideoUpload = multer({ storage: tempVideoStorage }).single("file");
const videoUpload = multer({ storage: videoStorage }).single("file");

// uploading multiple files using multer
function multipleFilesUpload(req, res, next) {
  videoUpload(req, res, next);
  tempVideoUpload(req, res, next);
}

app.post("/uploadVideo", multipleFilesUpload, (req, res) => {
  res.json({ file: req.file });
});

//-------------------------------------------------------------------------------//

// for uploading a single file

// app.post("/uploadVideo", (req, res) => {
//   videoUpload(req, res, (err) => {
//     if (err) {
//       return res.status(500).json(err);
//     }
//     return res.status(200).send(req.file);
//   });
// });

//-------------------------------------------------------------------------------//

// uploading audio files

var uploadAudioStorage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, "uploaded_audio/");
  },
  filename: (req, file, cb) => {
    cb(null, "audio.wav");
  },
});

var tempUploadAudioStorage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, "../client/src/denoised_uploaded_audio/");
  },
  filename: function (req, file, cb) {
    // file name
    cb(null, `inputUploadAudio.wav`);
  },
});

const tempAudioUpload = multer({ storage: tempUploadAudioStorage }).single(
  "file"
);
const audioUpload = multer({ storage: uploadAudioStorage }).single("file");

function multipleAudioFilesUpload(req, res, next) {
  tempAudioUpload(req, res, next);
  audioUpload(req, res, next);
}

app.post("/upload-audio", multipleAudioFilesUpload, (req, res) => {
  res.json({ file: req.file });
});

//-------------------------------------------------------------------------------//

// app.post("/upload-audio", (req, res) => {
//   audioUpload(req, res, (err) => {
//     if (err) {
//       return res.status(500).json(err);
//     }
//     return res.status(500).send(req.file);
//   });
// });

//-------------------------------------------------------------------------------//

// uploading recorded audio files
const storage = multer.diskStorage({
  destination(req, file, cb) {
    // directory to save the audio
    cb(null, "../client/src/denoised-audio/");
  },
  filename(req, file, cb) {
    const fileNameArr = file.originalname.split(".");
    // file name
    cb(null, `recording.${fileNameArr[fileNameArr.length - 1]}`);
  },
});

const upload = multer({ storage });

// const storage1 = multer.diskStorage({
//   destination(req, file, cb) {
//     // directory to save the audio
//     cb(null, "../client/src/denoised-audio/");
//   },
//   filename(req, file, cb) {
//     const fileNameArr = file.originalname.split(".");
//     // file name
//     cb(null, `inpur_recorded_audio.wav.${fileNameArr[fileNameArr.length - 1]}`);
//   },
// });

// const upload1 = multer({ storage1 });

// function multipleRecordedFilesUpload(req, res, next) {
//   upload(req, res, next);
//   upload1(req, res, next);
// }

app.post("/record", upload.single("audio"), (req, res) =>
  res.json({
    success: true,
  })
);

// UPLOADING VIDEO FILES
// var videoStorage = multer.diskStorage({
//   destination: function (req, file, cb) {
//     cb(null, "video_uploads");
//   },
//   filename: function (req, file, cb) {
//     cb(null, file.fieldname + "-" + ".mp4");
//   },
// });

// file size
// const maxSize = 1 * 1000000 * 1000000;

// var uploadvideo = multer({
//   storage: videoStorage,
//   limits: { fileSize: maxSize },
// fileFilter: function (req, file, cb) {
//   var filetypes = /jpeg|jpg|png/;
//   var mimetype = filetypes.test(file.mimetype);

//   var extname = filetypes.test(path.extname(file.originalname).toLowerCase());

//   if (mimetype && extname) {
//     return cb(null, true);
//   }

//   cb(
//     "Error: File upload only supports the " +
//       "following filetypes - " +
//       filetypes
//   );
// },
// }).single("newvideo");

// app.post("/uploadVideo", function (req, res, next) {
//   upload(req, res, function (er) {
//     if (err) {
//       res.send(err);
//     } else {
//       res.send("Video Uploaded");
//     }
//   });
// });

// running python files triggered from frontend

//------------------------------------------------------------------------------------------------------
function denoiseAudio(req, res) {
  // Use child_process.spawn method from
  // child_process module and assign it
  // to variable spawn
  var spawn = require("child_process").spawn;

  // spec
  // var process = spawn("python", ["denoising_by_specs_audio.py"]);

  // raw audio
  var process = spawn("python", ["denoising.py"]);

  process.stdout.on("data", function async(data) {
    // res.send(data.toString());
    console.log(data.toString());
  });
}
app.post("/denoise", denoiseAudio);

//------------------------------------------------------------------------------------------------------
// to denoise the video
function denoiseVideo(req, res) {
  var spawn = require("child_process").spawn;
  // spec
  // var process = spawn("python", ["denoising_by_specs.py"]);

  // raw audio
  var process = spawn("python", ["denoise_video.py"]);

  process.stdout.on("data", function async(data) {
    // res.send(data.toString());
    console.log(data.toString());
  });
}
app.post("/denoise-video", denoiseVideo);

//------------------------------------------------------------------------------------------------------
function denoiseUploadedAudio(req, res) {
  var spawn = require("child_process").spawn;
  var process = spawn("python", ["denoise_uploaded_audio_specs.py"]);
  // var process = spawn("python", ["denoise_uploaded_audio_raw.py"]);

  process.stdout.on("data", function async(data) {
    console.log(data.toString());
  });
}
app.post("/denoise-uploaded-audio", denoiseUploadedAudio);

//------------------------------------------------------------------------------------------------------

app.listen(8000, () => {
  console.log("server is running");
});
