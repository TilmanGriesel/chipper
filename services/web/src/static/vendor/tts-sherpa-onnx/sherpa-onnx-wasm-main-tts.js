var Module = typeof Module != "undefined" ? Module : {};
if (!Module.expectedDataFileDownloads) {
  Module.expectedDataFileDownloads = 0;
}
Module.expectedDataFileDownloads++;
(function () {
  if (Module["ENVIRONMENT_IS_PTHREAD"] || Module["$ww"]) return;
  var loadPackage = function (metadata) {
    var PACKAGE_PATH = "";
    if (typeof window === "object") {
      PACKAGE_PATH = window["encodeURIComponent"](
        window.location.pathname
          .toString()
          .substring(0, window.location.pathname.toString().lastIndexOf("/")) +
          "/"
      );
    } else if (
      typeof process === "undefined" &&
      typeof location !== "undefined"
    ) {
      PACKAGE_PATH = encodeURIComponent(
        location.pathname
          .toString()
          .substring(0, location.pathname.toString().lastIndexOf("/")) + "/"
      );
    }
    var PACKAGE_NAME = "../../bin/sherpa-onnx-wasm-main-tts.data";
    var REMOTE_PACKAGE_BASE = "sherpa-onnx-wasm-main-tts.data";
    if (
      typeof Module["locateFilePackage"] === "function" &&
      !Module["locateFile"]
    ) {
      Module["locateFile"] = Module["locateFilePackage"];
      err(
        "warning: you defined Module.locateFilePackage, that has been renamed to Module.locateFile (using your locateFilePackage for now)"
      );
    }
    var REMOTE_PACKAGE_NAME = Module["locateFile"]
      ? Module["locateFile"](REMOTE_PACKAGE_BASE, "")
      : REMOTE_PACKAGE_BASE;
    var REMOTE_PACKAGE_SIZE = metadata["remote_package_size"];
    function fetchRemotePackage(packageName, packageSize, callback, errback) {
      if (
        typeof process === "object" &&
        typeof process.versions === "object" &&
        typeof process.versions.node === "string"
      ) {
        require("fs").readFile(packageName, function (err, contents) {
          if (err) {
            errback(err);
          } else {
            callback(contents.buffer);
          }
        });
        return;
      }
      var xhr = new XMLHttpRequest();
      xhr.open("GET", packageName, true);
      xhr.responseType = "arraybuffer";
      xhr.onprogress = function (event) {
        var url = packageName;
        var size = packageSize;
        if (event.total) size = event.total;
        if (event.loaded) {
          if (!xhr.addedTotal) {
            xhr.addedTotal = true;
            if (!Module.dataFileDownloads) Module.dataFileDownloads = {};
            Module.dataFileDownloads[url] = {
              loaded: event.loaded,
              total: size,
            };
          } else {
            Module.dataFileDownloads[url].loaded = event.loaded;
          }
          var total = 0;
          var loaded = 0;
          var num = 0;
          for (var download in Module.dataFileDownloads) {
            var data = Module.dataFileDownloads[download];
            total += data.total;
            loaded += data.loaded;
            num++;
          }
          total = Math.ceil((total * Module.expectedDataFileDownloads) / num);
          if (Module["setStatus"])
            Module["setStatus"](`Downloading data... (${loaded}/${total})`);
        } else if (!Module.dataFileDownloads) {
          if (Module["setStatus"]) Module["setStatus"]("Downloading data...");
        }
      };
      xhr.onerror = function (event) {
        throw new Error("NetworkError for: " + packageName);
      };
      xhr.onload = function (event) {
        if (
          xhr.status == 200 ||
          xhr.status == 304 ||
          xhr.status == 206 ||
          (xhr.status == 0 && xhr.response)
        ) {
          var packageData = xhr.response;
          callback(packageData);
        } else {
          throw new Error(xhr.statusText + " : " + xhr.responseURL);
        }
      };
      xhr.send(null);
    }
    function handleError(error) {
      console.error("package error:", error);
    }
    var fetchedCallback = null;
    var fetched = Module["getPreloadedPackage"]
      ? Module["getPreloadedPackage"](REMOTE_PACKAGE_NAME, REMOTE_PACKAGE_SIZE)
      : null;
    if (!fetched)
      fetchRemotePackage(
        REMOTE_PACKAGE_NAME,
        REMOTE_PACKAGE_SIZE,
        function (data) {
          if (fetchedCallback) {
            fetchedCallback(data);
            fetchedCallback = null;
          } else {
            fetched = data;
          }
        },
        handleError
      );
    function runWithFS() {
      function assert(check, msg) {
        if (!check) throw msg + new Error().stack;
      }
      Module["FS_createPath"]("/", "espeak-ng-data", true, true);
      Module["FS_createPath"]("/espeak-ng-data", "lang", true, true);
      Module["FS_createPath"]("/espeak-ng-data/lang", "aav", true, true);
      Module["FS_createPath"]("/espeak-ng-data/lang", "art", true, true);
      Module["FS_createPath"]("/espeak-ng-data/lang", "azc", true, true);
      Module["FS_createPath"]("/espeak-ng-data/lang", "bat", true, true);
      Module["FS_createPath"]("/espeak-ng-data/lang", "bnt", true, true);
      Module["FS_createPath"]("/espeak-ng-data/lang", "ccs", true, true);
      Module["FS_createPath"]("/espeak-ng-data/lang", "cel", true, true);
      Module["FS_createPath"]("/espeak-ng-data/lang", "cus", true, true);
      Module["FS_createPath"]("/espeak-ng-data/lang", "dra", true, true);
      Module["FS_createPath"]("/espeak-ng-data/lang", "esx", true, true);
      Module["FS_createPath"]("/espeak-ng-data/lang", "gmq", true, true);
      Module["FS_createPath"]("/espeak-ng-data/lang", "gmw", true, true);
      Module["FS_createPath"]("/espeak-ng-data/lang", "grk", true, true);
      Module["FS_createPath"]("/espeak-ng-data/lang", "inc", true, true);
      Module["FS_createPath"]("/espeak-ng-data/lang", "ine", true, true);
      Module["FS_createPath"]("/espeak-ng-data/lang", "ira", true, true);
      Module["FS_createPath"]("/espeak-ng-data/lang", "iro", true, true);
      Module["FS_createPath"]("/espeak-ng-data/lang", "itc", true, true);
      Module["FS_createPath"]("/espeak-ng-data/lang", "jpx", true, true);
      Module["FS_createPath"]("/espeak-ng-data/lang", "map", true, true);
      Module["FS_createPath"]("/espeak-ng-data/lang", "miz", true, true);
      Module["FS_createPath"]("/espeak-ng-data/lang", "myn", true, true);
      Module["FS_createPath"]("/espeak-ng-data/lang", "poz", true, true);
      Module["FS_createPath"]("/espeak-ng-data/lang", "roa", true, true);
      Module["FS_createPath"]("/espeak-ng-data/lang", "sai", true, true);
      Module["FS_createPath"]("/espeak-ng-data/lang", "sem", true, true);
      Module["FS_createPath"]("/espeak-ng-data/lang", "sit", true, true);
      Module["FS_createPath"]("/espeak-ng-data/lang", "tai", true, true);
      Module["FS_createPath"]("/espeak-ng-data/lang", "trk", true, true);
      Module["FS_createPath"]("/espeak-ng-data/lang", "urj", true, true);
      Module["FS_createPath"]("/espeak-ng-data/lang", "zle", true, true);
      Module["FS_createPath"]("/espeak-ng-data/lang", "zls", true, true);
      Module["FS_createPath"]("/espeak-ng-data/lang", "zlw", true, true);
      Module["FS_createPath"]("/espeak-ng-data", "voices", true, true);
      Module["FS_createPath"]("/espeak-ng-data/voices", "!v", true, true);
      function DataRequest(start, end, audio) {
        this.start = start;
        this.end = end;
        this.audio = audio;
      }
      DataRequest.prototype = {
        requests: {},
        open: function (mode, name) {
          this.name = name;
          this.requests[name] = this;
          Module["addRunDependency"](`fp ${this.name}`);
        },
        send: function () {},
        onload: function () {
          var byteArray = this.byteArray.subarray(this.start, this.end);
          this.finish(byteArray);
        },
        finish: function (byteArray) {
          var that = this;
          Module["FS_createDataFile"](
            this.name,
            null,
            byteArray,
            true,
            true,
            true
          );
          Module["removeRunDependency"](`fp ${that.name}`);
          this.requests[this.name] = null;
        },
      };
      var files = metadata["files"];
      for (var i = 0; i < files.length; ++i) {
        new DataRequest(
          files[i]["start"],
          files[i]["end"],
          files[i]["audio"] || 0
        ).open("GET", files[i]["filename"]);
      }
      function processPackageData(arrayBuffer) {
        assert(arrayBuffer, "Loading data file failed.");
        assert(
          arrayBuffer.constructor.name === ArrayBuffer.name,
          "bad input to processPackageData"
        );
        var byteArray = new Uint8Array(arrayBuffer);
        DataRequest.prototype.byteArray = byteArray;
        var files = metadata["files"];
        for (var i = 0; i < files.length; ++i) {
          DataRequest.prototype.requests[files[i].filename].onload();
        }
        Module["removeRunDependency"](
          "datafile_../../bin/sherpa-onnx-wasm-main-tts.data"
        );
      }
      Module["addRunDependency"](
        "datafile_../../bin/sherpa-onnx-wasm-main-tts.data"
      );
      if (!Module.preloadResults) Module.preloadResults = {};
      Module.preloadResults[PACKAGE_NAME] = { fromCache: false };
      if (fetched) {
        processPackageData(fetched);
        fetched = null;
      } else {
        fetchedCallback = processPackageData;
      }
    }
    if (Module["calledRun"]) {
      runWithFS();
    } else {
      if (!Module["preRun"]) Module["preRun"] = [];
      Module["preRun"].push(runWithFS);
    }
  };
  loadPackage({
    files: [
      { filename: "/.gitignore", start: 0, end: 29 },
      { filename: "/README.md", start: 29, end: 1168 },
      { filename: "/espeak-ng-data/af_dict", start: 1168, end: 122641 },
      { filename: "/espeak-ng-data/am_dict", start: 122641, end: 186519 },
      { filename: "/espeak-ng-data/an_dict", start: 186519, end: 193210 },
      { filename: "/espeak-ng-data/ar_dict", start: 193210, end: 671375 },
      { filename: "/espeak-ng-data/as_dict", start: 671375, end: 676380 },
      { filename: "/espeak-ng-data/az_dict", start: 676380, end: 720153 },
      { filename: "/espeak-ng-data/ba_dict", start: 720153, end: 722251 },
      { filename: "/espeak-ng-data/be_dict", start: 722251, end: 724903 },
      { filename: "/espeak-ng-data/bg_dict", start: 724903, end: 811954 },
      { filename: "/espeak-ng-data/bn_dict", start: 811954, end: 901933 },
      { filename: "/espeak-ng-data/bpy_dict", start: 901933, end: 907159 },
      { filename: "/espeak-ng-data/bs_dict", start: 907159, end: 954227 },
      { filename: "/espeak-ng-data/ca_dict", start: 954227, end: 999793 },
      { filename: "/espeak-ng-data/chr_dict", start: 999793, end: 1002652 },
      { filename: "/espeak-ng-data/cmn_dict", start: 1002652, end: 2568987 },
      { filename: "/espeak-ng-data/cs_dict", start: 2568987, end: 2618632 },
      { filename: "/espeak-ng-data/cv_dict", start: 2618632, end: 2619976 },
      { filename: "/espeak-ng-data/cy_dict", start: 2619976, end: 2663106 },
      { filename: "/espeak-ng-data/da_dict", start: 2663106, end: 2908393 },
      { filename: "/espeak-ng-data/de_dict", start: 2908393, end: 2976669 },
      { filename: "/espeak-ng-data/el_dict", start: 2976669, end: 3049510 },
      { filename: "/espeak-ng-data/en_dict", start: 3049510, end: 3216454 },
      { filename: "/espeak-ng-data/eo_dict", start: 3216454, end: 3221120 },
      { filename: "/espeak-ng-data/es_dict", start: 3221120, end: 3270372 },
      { filename: "/espeak-ng-data/et_dict", start: 3270372, end: 3314635 },
      { filename: "/espeak-ng-data/eu_dict", start: 3314635, end: 3363476 },
      { filename: "/espeak-ng-data/fa_dict", start: 3363476, end: 3655899 },
      { filename: "/espeak-ng-data/fi_dict", start: 3655899, end: 3699827 },
      { filename: "/espeak-ng-data/fr_dict", start: 3699827, end: 3763554 },
      { filename: "/espeak-ng-data/ga_dict", start: 3763554, end: 3816227 },
      { filename: "/espeak-ng-data/gd_dict", start: 3816227, end: 3865348 },
      { filename: "/espeak-ng-data/gn_dict", start: 3865348, end: 3868596 },
      { filename: "/espeak-ng-data/grc_dict", start: 3868596, end: 3872029 },
      { filename: "/espeak-ng-data/gu_dict", start: 3872029, end: 3954509 },
      { filename: "/espeak-ng-data/hak_dict", start: 3954509, end: 3957844 },
      { filename: "/espeak-ng-data/haw_dict", start: 3957844, end: 3960287 },
      { filename: "/espeak-ng-data/he_dict", start: 3960287, end: 3967250 },
      { filename: "/espeak-ng-data/hi_dict", start: 3967250, end: 4059393 },
      { filename: "/espeak-ng-data/hr_dict", start: 4059393, end: 4108781 },
      { filename: "/espeak-ng-data/ht_dict", start: 4108781, end: 4110584 },
      { filename: "/espeak-ng-data/hu_dict", start: 4110584, end: 4264369 },
      { filename: "/espeak-ng-data/hy_dict", start: 4264369, end: 4326632 },
      { filename: "/espeak-ng-data/ia_dict", start: 4326632, end: 4657907 },
      { filename: "/espeak-ng-data/id_dict", start: 4657907, end: 4701365 },
      { filename: "/espeak-ng-data/intonations", start: 4701365, end: 4703405 },
      { filename: "/espeak-ng-data/io_dict", start: 4703405, end: 4705570 },
      { filename: "/espeak-ng-data/is_dict", start: 4705570, end: 4749924 },
      { filename: "/espeak-ng-data/it_dict", start: 4749924, end: 4902813 },
      { filename: "/espeak-ng-data/ja_dict", start: 4902813, end: 4950465 },
      { filename: "/espeak-ng-data/jbo_dict", start: 4950465, end: 4952708 },
      { filename: "/espeak-ng-data/ka_dict", start: 4952708, end: 5040483 },
      { filename: "/espeak-ng-data/kk_dict", start: 5040483, end: 5042342 },
      { filename: "/espeak-ng-data/kl_dict", start: 5042342, end: 5045180 },
      { filename: "/espeak-ng-data/kn_dict", start: 5045180, end: 5133008 },
      { filename: "/espeak-ng-data/ko_dict", start: 5133008, end: 5180531 },
      { filename: "/espeak-ng-data/kok_dict", start: 5180531, end: 5186925 },
      { filename: "/espeak-ng-data/ku_dict", start: 5186925, end: 5189190 },
      { filename: "/espeak-ng-data/ky_dict", start: 5189190, end: 5254167 },
      { filename: "/espeak-ng-data/la_dict", start: 5254167, end: 5257973 },
      { filename: "/espeak-ng-data/lang/aav/vi", start: 5257973, end: 5258084 },
      {
        filename: "/espeak-ng-data/lang/aav/vi-VN-x-central",
        start: 5258084,
        end: 5258227,
      },
      {
        filename: "/espeak-ng-data/lang/aav/vi-VN-x-south",
        start: 5258227,
        end: 5258369,
      },
      { filename: "/espeak-ng-data/lang/art/eo", start: 5258369, end: 5258410 },
      { filename: "/espeak-ng-data/lang/art/ia", start: 5258410, end: 5258439 },
      { filename: "/espeak-ng-data/lang/art/io", start: 5258439, end: 5258489 },
      {
        filename: "/espeak-ng-data/lang/art/jbo",
        start: 5258489,
        end: 5258558,
      },
      {
        filename: "/espeak-ng-data/lang/art/lfn",
        start: 5258558,
        end: 5258693,
      },
      {
        filename: "/espeak-ng-data/lang/art/piqd",
        start: 5258693,
        end: 5258749,
      },
      { filename: "/espeak-ng-data/lang/art/py", start: 5258749, end: 5258889 },
      {
        filename: "/espeak-ng-data/lang/art/qdb",
        start: 5258889,
        end: 5258946,
      },
      {
        filename: "/espeak-ng-data/lang/art/qya",
        start: 5258946,
        end: 5259119,
      },
      {
        filename: "/espeak-ng-data/lang/art/sjn",
        start: 5259119,
        end: 5259294,
      },
      {
        filename: "/espeak-ng-data/lang/azc/nci",
        start: 5259294,
        end: 5259408,
      },
      { filename: "/espeak-ng-data/lang/bat/lt", start: 5259408, end: 5259436 },
      {
        filename: "/espeak-ng-data/lang/bat/ltg",
        start: 5259436,
        end: 5259748,
      },
      { filename: "/espeak-ng-data/lang/bat/lv", start: 5259748, end: 5259977 },
      { filename: "/espeak-ng-data/lang/bnt/sw", start: 5259977, end: 5260018 },
      { filename: "/espeak-ng-data/lang/bnt/tn", start: 5260018, end: 5260060 },
      { filename: "/espeak-ng-data/lang/ccs/ka", start: 5260060, end: 5260184 },
      { filename: "/espeak-ng-data/lang/cel/cy", start: 5260184, end: 5260221 },
      { filename: "/espeak-ng-data/lang/cel/ga", start: 5260221, end: 5260287 },
      { filename: "/espeak-ng-data/lang/cel/gd", start: 5260287, end: 5260338 },
      { filename: "/espeak-ng-data/lang/cus/om", start: 5260338, end: 5260377 },
      { filename: "/espeak-ng-data/lang/dra/kn", start: 5260377, end: 5260432 },
      { filename: "/espeak-ng-data/lang/dra/ml", start: 5260432, end: 5260489 },
      { filename: "/espeak-ng-data/lang/dra/ta", start: 5260489, end: 5260540 },
      { filename: "/espeak-ng-data/lang/dra/te", start: 5260540, end: 5260610 },
      { filename: "/espeak-ng-data/lang/esx/kl", start: 5260610, end: 5260640 },
      { filename: "/espeak-ng-data/lang/eu", start: 5260640, end: 5260694 },
      { filename: "/espeak-ng-data/lang/gmq/da", start: 5260694, end: 5260737 },
      { filename: "/espeak-ng-data/lang/gmq/is", start: 5260737, end: 5260764 },
      { filename: "/espeak-ng-data/lang/gmq/nb", start: 5260764, end: 5260851 },
      { filename: "/espeak-ng-data/lang/gmq/sv", start: 5260851, end: 5260876 },
      { filename: "/espeak-ng-data/lang/gmw/af", start: 5260876, end: 5260999 },
      { filename: "/espeak-ng-data/lang/gmw/de", start: 5260999, end: 5261041 },
      { filename: "/espeak-ng-data/lang/gmw/en", start: 5261041, end: 5261181 },
      {
        filename: "/espeak-ng-data/lang/gmw/en-029",
        start: 5261181,
        end: 5261516,
      },
      {
        filename: "/espeak-ng-data/lang/gmw/en-GB-scotland",
        start: 5261516,
        end: 5261811,
      },
      {
        filename: "/espeak-ng-data/lang/gmw/en-GB-x-gbclan",
        start: 5261811,
        end: 5262049,
      },
      {
        filename: "/espeak-ng-data/lang/gmw/en-GB-x-gbcwmd",
        start: 5262049,
        end: 5262237,
      },
      {
        filename: "/espeak-ng-data/lang/gmw/en-GB-x-rp",
        start: 5262237,
        end: 5262486,
      },
      {
        filename: "/espeak-ng-data/lang/gmw/en-US",
        start: 5262486,
        end: 5262743,
      },
      {
        filename: "/espeak-ng-data/lang/gmw/en-US-nyc",
        start: 5262743,
        end: 5263014,
      },
      { filename: "/espeak-ng-data/lang/gmw/lb", start: 5263014, end: 5263045 },
      { filename: "/espeak-ng-data/lang/gmw/nl", start: 5263045, end: 5263068 },
      { filename: "/espeak-ng-data/lang/grk/el", start: 5263068, end: 5263091 },
      {
        filename: "/espeak-ng-data/lang/grk/grc",
        start: 5263091,
        end: 5263190,
      },
      { filename: "/espeak-ng-data/lang/inc/as", start: 5263190, end: 5263232 },
      { filename: "/espeak-ng-data/lang/inc/bn", start: 5263232, end: 5263257 },
      {
        filename: "/espeak-ng-data/lang/inc/bpy",
        start: 5263257,
        end: 5263296,
      },
      { filename: "/espeak-ng-data/lang/inc/gu", start: 5263296, end: 5263338 },
      { filename: "/espeak-ng-data/lang/inc/hi", start: 5263338, end: 5263361 },
      {
        filename: "/espeak-ng-data/lang/inc/kok",
        start: 5263361,
        end: 5263387,
      },
      { filename: "/espeak-ng-data/lang/inc/mr", start: 5263387, end: 5263428 },
      { filename: "/espeak-ng-data/lang/inc/ne", start: 5263428, end: 5263465 },
      { filename: "/espeak-ng-data/lang/inc/or", start: 5263465, end: 5263504 },
      { filename: "/espeak-ng-data/lang/inc/pa", start: 5263504, end: 5263529 },
      { filename: "/espeak-ng-data/lang/inc/sd", start: 5263529, end: 5263595 },
      { filename: "/espeak-ng-data/lang/inc/si", start: 5263595, end: 5263650 },
      { filename: "/espeak-ng-data/lang/inc/ur", start: 5263650, end: 5263744 },
      { filename: "/espeak-ng-data/lang/ine/hy", start: 5263744, end: 5263805 },
      {
        filename: "/espeak-ng-data/lang/ine/hyw",
        start: 5263805,
        end: 5264170,
      },
      { filename: "/espeak-ng-data/lang/ine/sq", start: 5264170, end: 5264273 },
      { filename: "/espeak-ng-data/lang/ira/fa", start: 5264273, end: 5264363 },
      {
        filename: "/espeak-ng-data/lang/ira/fa-Latn",
        start: 5264363,
        end: 5264632,
      },
      { filename: "/espeak-ng-data/lang/ira/ku", start: 5264632, end: 5264672 },
      {
        filename: "/espeak-ng-data/lang/iro/chr",
        start: 5264672,
        end: 5265241,
      },
      { filename: "/espeak-ng-data/lang/itc/la", start: 5265241, end: 5265538 },
      { filename: "/espeak-ng-data/lang/jpx/ja", start: 5265538, end: 5265590 },
      { filename: "/espeak-ng-data/lang/ko", start: 5265590, end: 5265641 },
      {
        filename: "/espeak-ng-data/lang/map/haw",
        start: 5265641,
        end: 5265683,
      },
      {
        filename: "/espeak-ng-data/lang/miz/mto",
        start: 5265683,
        end: 5265866,
      },
      {
        filename: "/espeak-ng-data/lang/myn/quc",
        start: 5265866,
        end: 5266076,
      },
      { filename: "/espeak-ng-data/lang/poz/id", start: 5266076, end: 5266210 },
      { filename: "/espeak-ng-data/lang/poz/mi", start: 5266210, end: 5266577 },
      { filename: "/espeak-ng-data/lang/poz/ms", start: 5266577, end: 5267007 },
      { filename: "/espeak-ng-data/lang/qu", start: 5267007, end: 5267095 },
      { filename: "/espeak-ng-data/lang/roa/an", start: 5267095, end: 5267122 },
      { filename: "/espeak-ng-data/lang/roa/ca", start: 5267122, end: 5267147 },
      { filename: "/espeak-ng-data/lang/roa/es", start: 5267147, end: 5267210 },
      {
        filename: "/espeak-ng-data/lang/roa/es-419",
        start: 5267210,
        end: 5267377,
      },
      { filename: "/espeak-ng-data/lang/roa/fr", start: 5267377, end: 5267456 },
      {
        filename: "/espeak-ng-data/lang/roa/fr-BE",
        start: 5267456,
        end: 5267540,
      },
      {
        filename: "/espeak-ng-data/lang/roa/fr-CH",
        start: 5267540,
        end: 5267626,
      },
      { filename: "/espeak-ng-data/lang/roa/ht", start: 5267626, end: 5267766 },
      { filename: "/espeak-ng-data/lang/roa/it", start: 5267766, end: 5267875 },
      {
        filename: "/espeak-ng-data/lang/roa/pap",
        start: 5267875,
        end: 5267937,
      },
      { filename: "/espeak-ng-data/lang/roa/pt", start: 5267937, end: 5268032 },
      {
        filename: "/espeak-ng-data/lang/roa/pt-BR",
        start: 5268032,
        end: 5268141,
      },
      { filename: "/espeak-ng-data/lang/roa/ro", start: 5268141, end: 5268167 },
      { filename: "/espeak-ng-data/lang/sai/gn", start: 5268167, end: 5268214 },
      { filename: "/espeak-ng-data/lang/sem/am", start: 5268214, end: 5268255 },
      { filename: "/espeak-ng-data/lang/sem/ar", start: 5268255, end: 5268305 },
      { filename: "/espeak-ng-data/lang/sem/he", start: 5268305, end: 5268345 },
      { filename: "/espeak-ng-data/lang/sem/mt", start: 5268345, end: 5268386 },
      {
        filename: "/espeak-ng-data/lang/sit/cmn",
        start: 5268386,
        end: 5269072,
      },
      {
        filename: "/espeak-ng-data/lang/sit/cmn-Latn-pinyin",
        start: 5269072,
        end: 5269233,
      },
      {
        filename: "/espeak-ng-data/lang/sit/hak",
        start: 5269233,
        end: 5269361,
      },
      { filename: "/espeak-ng-data/lang/sit/my", start: 5269361, end: 5269417 },
      {
        filename: "/espeak-ng-data/lang/sit/yue",
        start: 5269417,
        end: 5269611,
      },
      {
        filename: "/espeak-ng-data/lang/sit/yue-Latn-jyutping",
        start: 5269611,
        end: 5269824,
      },
      {
        filename: "/espeak-ng-data/lang/tai/shn",
        start: 5269824,
        end: 5269916,
      },
      { filename: "/espeak-ng-data/lang/tai/th", start: 5269916, end: 5269953 },
      { filename: "/espeak-ng-data/lang/trk/az", start: 5269953, end: 5269998 },
      { filename: "/espeak-ng-data/lang/trk/ba", start: 5269998, end: 5270023 },
      { filename: "/espeak-ng-data/lang/trk/cv", start: 5270023, end: 5270063 },
      { filename: "/espeak-ng-data/lang/trk/kk", start: 5270063, end: 5270103 },
      { filename: "/espeak-ng-data/lang/trk/ky", start: 5270103, end: 5270146 },
      {
        filename: "/espeak-ng-data/lang/trk/nog",
        start: 5270146,
        end: 5270185,
      },
      { filename: "/espeak-ng-data/lang/trk/tk", start: 5270185, end: 5270210 },
      { filename: "/espeak-ng-data/lang/trk/tr", start: 5270210, end: 5270235 },
      { filename: "/espeak-ng-data/lang/trk/tt", start: 5270235, end: 5270258 },
      { filename: "/espeak-ng-data/lang/trk/ug", start: 5270258, end: 5270282 },
      { filename: "/espeak-ng-data/lang/trk/uz", start: 5270282, end: 5270321 },
      { filename: "/espeak-ng-data/lang/urj/et", start: 5270321, end: 5270558 },
      { filename: "/espeak-ng-data/lang/urj/fi", start: 5270558, end: 5270795 },
      { filename: "/espeak-ng-data/lang/urj/hu", start: 5270795, end: 5270868 },
      {
        filename: "/espeak-ng-data/lang/urj/smj",
        start: 5270868,
        end: 5270913,
      },
      { filename: "/espeak-ng-data/lang/zle/be", start: 5270913, end: 5270965 },
      { filename: "/espeak-ng-data/lang/zle/ru", start: 5270965, end: 5271022 },
      {
        filename: "/espeak-ng-data/lang/zle/ru-LV",
        start: 5271022,
        end: 5271302,
      },
      {
        filename: "/espeak-ng-data/lang/zle/ru-cl",
        start: 5271302,
        end: 5271393,
      },
      { filename: "/espeak-ng-data/lang/zle/uk", start: 5271393, end: 5271490 },
      { filename: "/espeak-ng-data/lang/zls/bg", start: 5271490, end: 5271601 },
      { filename: "/espeak-ng-data/lang/zls/bs", start: 5271601, end: 5271831 },
      { filename: "/espeak-ng-data/lang/zls/hr", start: 5271831, end: 5272093 },
      { filename: "/espeak-ng-data/lang/zls/mk", start: 5272093, end: 5272121 },
      { filename: "/espeak-ng-data/lang/zls/sl", start: 5272121, end: 5272164 },
      { filename: "/espeak-ng-data/lang/zls/sr", start: 5272164, end: 5272414 },
      { filename: "/espeak-ng-data/lang/zlw/cs", start: 5272414, end: 5272437 },
      { filename: "/espeak-ng-data/lang/zlw/pl", start: 5272437, end: 5272475 },
      { filename: "/espeak-ng-data/lang/zlw/sk", start: 5272475, end: 5272499 },
      { filename: "/espeak-ng-data/lb_dict", start: 5272499, end: 5960430 },
      { filename: "/espeak-ng-data/lfn_dict", start: 5960430, end: 5963223 },
      { filename: "/espeak-ng-data/lt_dict", start: 5963223, end: 6013113 },
      { filename: "/espeak-ng-data/lv_dict", start: 6013113, end: 6079450 },
      { filename: "/espeak-ng-data/mi_dict", start: 6079450, end: 6080796 },
      { filename: "/espeak-ng-data/mk_dict", start: 6080796, end: 6144655 },
      { filename: "/espeak-ng-data/ml_dict", start: 6144655, end: 6237e3 },
      { filename: "/espeak-ng-data/mr_dict", start: 6237e3, end: 6324391 },
      { filename: "/espeak-ng-data/ms_dict", start: 6324391, end: 6377932 },
      { filename: "/espeak-ng-data/mt_dict", start: 6377932, end: 6382316 },
      { filename: "/espeak-ng-data/mto_dict", start: 6382316, end: 6386276 },
      { filename: "/espeak-ng-data/my_dict", start: 6386276, end: 6482224 },
      { filename: "/espeak-ng-data/nci_dict", start: 6482224, end: 6483758 },
      { filename: "/espeak-ng-data/ne_dict", start: 6483758, end: 6579135 },
      { filename: "/espeak-ng-data/nl_dict", start: 6579135, end: 6645114 },
      { filename: "/espeak-ng-data/no_dict", start: 6645114, end: 6649292 },
      { filename: "/espeak-ng-data/nog_dict", start: 6649292, end: 6652586 },
      { filename: "/espeak-ng-data/om_dict", start: 6652586, end: 6654888 },
      { filename: "/espeak-ng-data/or_dict", start: 6654888, end: 6744134 },
      { filename: "/espeak-ng-data/pa_dict", start: 6744134, end: 6824087 },
      { filename: "/espeak-ng-data/pap_dict", start: 6824087, end: 6826215 },
      { filename: "/espeak-ng-data/phondata", start: 6826215, end: 7376639 },
      {
        filename: "/espeak-ng-data/phondata-manifest",
        start: 7376639,
        end: 7398460,
      },
      { filename: "/espeak-ng-data/phonindex", start: 7398460, end: 7437534 },
      { filename: "/espeak-ng-data/phontab", start: 7437534, end: 7493330 },
      { filename: "/espeak-ng-data/piqd_dict", start: 7493330, end: 7495040 },
      { filename: "/espeak-ng-data/pl_dict", start: 7495040, end: 7571770 },
      { filename: "/espeak-ng-data/pt_dict", start: 7571770, end: 7639587 },
      { filename: "/espeak-ng-data/py_dict", start: 7639587, end: 7641996 },
      { filename: "/espeak-ng-data/qdb_dict", start: 7641996, end: 7645024 },
      { filename: "/espeak-ng-data/qu_dict", start: 7645024, end: 7646943 },
      { filename: "/espeak-ng-data/quc_dict", start: 7646943, end: 7648393 },
      { filename: "/espeak-ng-data/qya_dict", start: 7648393, end: 7650332 },
      { filename: "/espeak-ng-data/ro_dict", start: 7650332, end: 7718870 },
      { filename: "/espeak-ng-data/ru_dict", start: 7718870, end: 16251262 },
      { filename: "/espeak-ng-data/sd_dict", start: 16251262, end: 16311190 },
      { filename: "/espeak-ng-data/shn_dict", start: 16311190, end: 16399362 },
      { filename: "/espeak-ng-data/si_dict", start: 16399362, end: 16484746 },
      { filename: "/espeak-ng-data/sjn_dict", start: 16484746, end: 16486529 },
      { filename: "/espeak-ng-data/sk_dict", start: 16486529, end: 16536531 },
      { filename: "/espeak-ng-data/sl_dict", start: 16536531, end: 16581578 },
      { filename: "/espeak-ng-data/smj_dict", start: 16581578, end: 16616673 },
      { filename: "/espeak-ng-data/sq_dict", start: 16616673, end: 16661676 },
      { filename: "/espeak-ng-data/sr_dict", start: 16661676, end: 16708508 },
      { filename: "/espeak-ng-data/sv_dict", start: 16708508, end: 16756344 },
      { filename: "/espeak-ng-data/sw_dict", start: 16756344, end: 16804148 },
      { filename: "/espeak-ng-data/ta_dict", start: 16804148, end: 17013701 },
      { filename: "/espeak-ng-data/te_dict", start: 17013701, end: 17108538 },
      { filename: "/espeak-ng-data/th_dict", start: 17108538, end: 17110839 },
      { filename: "/espeak-ng-data/tk_dict", start: 17110839, end: 17131707 },
      { filename: "/espeak-ng-data/tn_dict", start: 17131707, end: 17134779 },
      { filename: "/espeak-ng-data/tr_dict", start: 17134779, end: 17181572 },
      { filename: "/espeak-ng-data/tt_dict", start: 17181572, end: 17183693 },
      { filename: "/espeak-ng-data/ug_dict", start: 17183693, end: 17185763 },
      { filename: "/espeak-ng-data/uk_dict", start: 17185763, end: 17189255 },
      { filename: "/espeak-ng-data/ur_dict", start: 17189255, end: 17322811 },
      { filename: "/espeak-ng-data/uz_dict", start: 17322811, end: 17325351 },
      { filename: "/espeak-ng-data/vi_dict", start: 17325351, end: 17377959 },
      {
        filename: "/espeak-ng-data/voices/!v/Alex",
        start: 17377959,
        end: 17378087,
      },
      {
        filename: "/espeak-ng-data/voices/!v/Alicia",
        start: 17378087,
        end: 17378561,
      },
      {
        filename: "/espeak-ng-data/voices/!v/Andrea",
        start: 17378561,
        end: 17378918,
      },
      {
        filename: "/espeak-ng-data/voices/!v/Andy",
        start: 17378918,
        end: 17379238,
      },
      {
        filename: "/espeak-ng-data/voices/!v/Annie",
        start: 17379238,
        end: 17379553,
      },
      {
        filename: "/espeak-ng-data/voices/!v/AnxiousAndy",
        start: 17379553,
        end: 17379914,
      },
      {
        filename: "/espeak-ng-data/voices/!v/Demonic",
        start: 17379914,
        end: 17383772,
      },
      {
        filename: "/espeak-ng-data/voices/!v/Denis",
        start: 17383772,
        end: 17384077,
      },
      {
        filename: "/espeak-ng-data/voices/!v/Diogo",
        start: 17384077,
        end: 17384456,
      },
      {
        filename: "/espeak-ng-data/voices/!v/Gene",
        start: 17384456,
        end: 17384737,
      },
      {
        filename: "/espeak-ng-data/voices/!v/Gene2",
        start: 17384737,
        end: 17385020,
      },
      {
        filename: "/espeak-ng-data/voices/!v/Henrique",
        start: 17385020,
        end: 17385401,
      },
      {
        filename: "/espeak-ng-data/voices/!v/Hugo",
        start: 17385401,
        end: 17385779,
      },
      {
        filename: "/espeak-ng-data/voices/!v/Jacky",
        start: 17385779,
        end: 17386046,
      },
      {
        filename: "/espeak-ng-data/voices/!v/Lee",
        start: 17386046,
        end: 17386384,
      },
      {
        filename: "/espeak-ng-data/voices/!v/Marco",
        start: 17386384,
        end: 17386851,
      },
      {
        filename: "/espeak-ng-data/voices/!v/Mario",
        start: 17386851,
        end: 17387121,
      },
      {
        filename: "/espeak-ng-data/voices/!v/Michael",
        start: 17387121,
        end: 17387391,
      },
      {
        filename: "/espeak-ng-data/voices/!v/Mike",
        start: 17387391,
        end: 17387503,
      },
      {
        filename: "/espeak-ng-data/voices/!v/Mr serious",
        start: 17387503,
        end: 17390696,
      },
      {
        filename: "/espeak-ng-data/voices/!v/Nguyen",
        start: 17390696,
        end: 17390976,
      },
      {
        filename: "/espeak-ng-data/voices/!v/Reed",
        start: 17390976,
        end: 17391178,
      },
      {
        filename: "/espeak-ng-data/voices/!v/RicishayMax",
        start: 17391178,
        end: 17391411,
      },
      {
        filename: "/espeak-ng-data/voices/!v/RicishayMax2",
        start: 17391411,
        end: 17391846,
      },
      {
        filename: "/espeak-ng-data/voices/!v/RicishayMax3",
        start: 17391846,
        end: 17392281,
      },
      {
        filename: "/espeak-ng-data/voices/!v/Storm",
        start: 17392281,
        end: 17392701,
      },
      {
        filename: "/espeak-ng-data/voices/!v/Tweaky",
        start: 17392701,
        end: 17395890,
      },
      {
        filename: "/espeak-ng-data/voices/!v/UniRobot",
        start: 17395890,
        end: 17396307,
      },
      {
        filename: "/espeak-ng-data/voices/!v/adam",
        start: 17396307,
        end: 17396382,
      },
      {
        filename: "/espeak-ng-data/voices/!v/anika",
        start: 17396382,
        end: 17396875,
      },
      {
        filename: "/espeak-ng-data/voices/!v/anikaRobot",
        start: 17396875,
        end: 17397387,
      },
      {
        filename: "/espeak-ng-data/voices/!v/announcer",
        start: 17397387,
        end: 17397687,
      },
      {
        filename: "/espeak-ng-data/voices/!v/antonio",
        start: 17397687,
        end: 17398068,
      },
      {
        filename: "/espeak-ng-data/voices/!v/aunty",
        start: 17398068,
        end: 17398426,
      },
      {
        filename: "/espeak-ng-data/voices/!v/belinda",
        start: 17398426,
        end: 17398766,
      },
      {
        filename: "/espeak-ng-data/voices/!v/benjamin",
        start: 17398766,
        end: 17398967,
      },
      {
        filename: "/espeak-ng-data/voices/!v/boris",
        start: 17398967,
        end: 17399191,
      },
      {
        filename: "/espeak-ng-data/voices/!v/caleb",
        start: 17399191,
        end: 17399248,
      },
      {
        filename: "/espeak-ng-data/voices/!v/croak",
        start: 17399248,
        end: 17399341,
      },
      {
        filename: "/espeak-ng-data/voices/!v/david",
        start: 17399341,
        end: 17399453,
      },
      {
        filename: "/espeak-ng-data/voices/!v/ed",
        start: 17399453,
        end: 17399740,
      },
      {
        filename: "/espeak-ng-data/voices/!v/edward",
        start: 17399740,
        end: 17399891,
      },
      {
        filename: "/espeak-ng-data/voices/!v/edward2",
        start: 17399891,
        end: 17400043,
      },
      {
        filename: "/espeak-ng-data/voices/!v/f1",
        start: 17400043,
        end: 17400367,
      },
      {
        filename: "/espeak-ng-data/voices/!v/f2",
        start: 17400367,
        end: 17400724,
      },
      {
        filename: "/espeak-ng-data/voices/!v/f3",
        start: 17400724,
        end: 17401099,
      },
      {
        filename: "/espeak-ng-data/voices/!v/f4",
        start: 17401099,
        end: 17401449,
      },
      {
        filename: "/espeak-ng-data/voices/!v/f5",
        start: 17401449,
        end: 17401881,
      },
      {
        filename: "/espeak-ng-data/voices/!v/fast",
        start: 17401881,
        end: 17402030,
      },
      {
        filename: "/espeak-ng-data/voices/!v/grandma",
        start: 17402030,
        end: 17402293,
      },
      {
        filename: "/espeak-ng-data/voices/!v/grandpa",
        start: 17402293,
        end: 17402549,
      },
      {
        filename: "/espeak-ng-data/voices/!v/gustave",
        start: 17402549,
        end: 17402802,
      },
      {
        filename: "/espeak-ng-data/voices/!v/ian",
        start: 17402802,
        end: 17405970,
      },
      {
        filename: "/espeak-ng-data/voices/!v/iven",
        start: 17405970,
        end: 17406231,
      },
      {
        filename: "/espeak-ng-data/voices/!v/iven2",
        start: 17406231,
        end: 17406510,
      },
      {
        filename: "/espeak-ng-data/voices/!v/iven3",
        start: 17406510,
        end: 17406772,
      },
      {
        filename: "/espeak-ng-data/voices/!v/iven4",
        start: 17406772,
        end: 17407033,
      },
      {
        filename: "/espeak-ng-data/voices/!v/john",
        start: 17407033,
        end: 17410219,
      },
      {
        filename: "/espeak-ng-data/voices/!v/kaukovalta",
        start: 17410219,
        end: 17410580,
      },
      {
        filename: "/espeak-ng-data/voices/!v/klatt",
        start: 17410580,
        end: 17410618,
      },
      {
        filename: "/espeak-ng-data/voices/!v/klatt2",
        start: 17410618,
        end: 17410656,
      },
      {
        filename: "/espeak-ng-data/voices/!v/klatt3",
        start: 17410656,
        end: 17410695,
      },
      {
        filename: "/espeak-ng-data/voices/!v/klatt4",
        start: 17410695,
        end: 17410734,
      },
      {
        filename: "/espeak-ng-data/voices/!v/klatt5",
        start: 17410734,
        end: 17410773,
      },
      {
        filename: "/espeak-ng-data/voices/!v/klatt6",
        start: 17410773,
        end: 17410812,
      },
      {
        filename: "/espeak-ng-data/voices/!v/linda",
        start: 17410812,
        end: 17411162,
      },
      {
        filename: "/espeak-ng-data/voices/!v/m1",
        start: 17411162,
        end: 17411497,
      },
      {
        filename: "/espeak-ng-data/voices/!v/m2",
        start: 17411497,
        end: 17411761,
      },
      {
        filename: "/espeak-ng-data/voices/!v/m3",
        start: 17411761,
        end: 17412061,
      },
      {
        filename: "/espeak-ng-data/voices/!v/m4",
        start: 17412061,
        end: 17412351,
      },
      {
        filename: "/espeak-ng-data/voices/!v/m5",
        start: 17412351,
        end: 17412613,
      },
      {
        filename: "/espeak-ng-data/voices/!v/m6",
        start: 17412613,
        end: 17412801,
      },
      {
        filename: "/espeak-ng-data/voices/!v/m7",
        start: 17412801,
        end: 17413055,
      },
      {
        filename: "/espeak-ng-data/voices/!v/m8",
        start: 17413055,
        end: 17413339,
      },
      {
        filename: "/espeak-ng-data/voices/!v/marcelo",
        start: 17413339,
        end: 17413590,
      },
      {
        filename: "/espeak-ng-data/voices/!v/max",
        start: 17413590,
        end: 17413815,
      },
      {
        filename: "/espeak-ng-data/voices/!v/michel",
        start: 17413815,
        end: 17414219,
      },
      {
        filename: "/espeak-ng-data/voices/!v/miguel",
        start: 17414219,
        end: 17414601,
      },
      {
        filename: "/espeak-ng-data/voices/!v/mike2",
        start: 17414601,
        end: 17414789,
      },
      {
        filename: "/espeak-ng-data/voices/!v/norbert",
        start: 17414789,
        end: 17417978,
      },
      {
        filename: "/espeak-ng-data/voices/!v/pablo",
        start: 17417978,
        end: 17421120,
      },
      {
        filename: "/espeak-ng-data/voices/!v/paul",
        start: 17421120,
        end: 17421404,
      },
      {
        filename: "/espeak-ng-data/voices/!v/pedro",
        start: 17421404,
        end: 17421756,
      },
      {
        filename: "/espeak-ng-data/voices/!v/quincy",
        start: 17421756,
        end: 17422110,
      },
      {
        filename: "/espeak-ng-data/voices/!v/rob",
        start: 17422110,
        end: 17422375,
      },
      {
        filename: "/espeak-ng-data/voices/!v/robert",
        start: 17422375,
        end: 17422649,
      },
      {
        filename: "/espeak-ng-data/voices/!v/robosoft",
        start: 17422649,
        end: 17423100,
      },
      {
        filename: "/espeak-ng-data/voices/!v/robosoft2",
        start: 17423100,
        end: 17423554,
      },
      {
        filename: "/espeak-ng-data/voices/!v/robosoft3",
        start: 17423554,
        end: 17424009,
      },
      {
        filename: "/espeak-ng-data/voices/!v/robosoft4",
        start: 17424009,
        end: 17424456,
      },
      {
        filename: "/espeak-ng-data/voices/!v/robosoft5",
        start: 17424456,
        end: 17424901,
      },
      {
        filename: "/espeak-ng-data/voices/!v/robosoft6",
        start: 17424901,
        end: 17425188,
      },
      {
        filename: "/espeak-ng-data/voices/!v/robosoft7",
        start: 17425188,
        end: 17425598,
      },
      {
        filename: "/espeak-ng-data/voices/!v/robosoft8",
        start: 17425598,
        end: 17425841,
      },
      {
        filename: "/espeak-ng-data/voices/!v/sandro",
        start: 17425841,
        end: 17426371,
      },
      {
        filename: "/espeak-ng-data/voices/!v/shelby",
        start: 17426371,
        end: 17426651,
      },
      {
        filename: "/espeak-ng-data/voices/!v/steph",
        start: 17426651,
        end: 17427015,
      },
      {
        filename: "/espeak-ng-data/voices/!v/steph2",
        start: 17427015,
        end: 17427382,
      },
      {
        filename: "/espeak-ng-data/voices/!v/steph3",
        start: 17427382,
        end: 17427759,
      },
      {
        filename: "/espeak-ng-data/voices/!v/travis",
        start: 17427759,
        end: 17428142,
      },
      {
        filename: "/espeak-ng-data/voices/!v/victor",
        start: 17428142,
        end: 17428395,
      },
      {
        filename: "/espeak-ng-data/voices/!v/whisper",
        start: 17428395,
        end: 17428581,
      },
      {
        filename: "/espeak-ng-data/voices/!v/whisperf",
        start: 17428581,
        end: 17428973,
      },
      {
        filename: "/espeak-ng-data/voices/!v/zac",
        start: 17428973,
        end: 17429248,
      },
      { filename: "/espeak-ng-data/yue_dict", start: 17429248, end: 17992819 },
      { filename: "/model.onnx", start: 17992819, end: 96573866 },
      { filename: "/tokens.txt", start: 96573866, end: 96574820 },
    ],
    remote_package_size: 96574820,
  });
})();
var moduleOverrides = Object.assign({}, Module);
var arguments_ = [];
var thisProgram = "./this.program";
var quit_ = (status, toThrow) => {
  throw toThrow;
};
var ENVIRONMENT_IS_WEB = typeof window == "object";
var ENVIRONMENT_IS_WORKER = typeof importScripts == "function";
var ENVIRONMENT_IS_NODE =
  typeof process == "object" &&
  typeof process.versions == "object" &&
  typeof process.versions.node == "string";
var scriptDirectory = "";
function locateFile(path) {
  if (Module["locateFile"]) {
    return Module["locateFile"](path, scriptDirectory);
  }
  return scriptDirectory + path;
}
var read_, readAsync, readBinary;
if (ENVIRONMENT_IS_NODE) {
  var fs = require("fs");
  var nodePath = require("path");
  if (ENVIRONMENT_IS_WORKER) {
    scriptDirectory = nodePath.dirname(scriptDirectory) + "/";
  } else {
    scriptDirectory = __dirname + "/";
  }
  read_ = (filename, binary) => {
    filename = isFileURI(filename)
      ? new URL(filename)
      : nodePath.normalize(filename);
    return fs.readFileSync(filename, binary ? undefined : "utf8");
  };
  readBinary = (filename) => {
    var ret = read_(filename, true);
    if (!ret.buffer) {
      ret = new Uint8Array(ret);
    }
    return ret;
  };
  readAsync = (filename, onload, onerror, binary = true) => {
    filename = isFileURI(filename)
      ? new URL(filename)
      : nodePath.normalize(filename);
    fs.readFile(filename, binary ? undefined : "utf8", (err, data) => {
      if (err) onerror(err);
      else onload(binary ? data.buffer : data);
    });
  };
  if (!Module["thisProgram"] && process.argv.length > 1) {
    thisProgram = process.argv[1].replace(/\\/g, "/");
  }
  arguments_ = process.argv.slice(2);
  if (typeof module != "undefined") {
    module["exports"] = Module;
  }
  process.on("uncaughtException", (ex) => {
    if (
      ex !== "unwind" &&
      !(ex instanceof ExitStatus) &&
      !(ex.context instanceof ExitStatus)
    ) {
      throw ex;
    }
  });
  quit_ = (status, toThrow) => {
    process.exitCode = status;
    throw toThrow;
  };
} else if (ENVIRONMENT_IS_WEB || ENVIRONMENT_IS_WORKER) {
  if (ENVIRONMENT_IS_WORKER) {
    scriptDirectory = self.location.href;
  } else if (typeof document != "undefined" && document.currentScript) {
    scriptDirectory = document.currentScript.src;
  }
  if (scriptDirectory.startsWith("blob:")) {
    scriptDirectory = "";
  } else {
    scriptDirectory = scriptDirectory.substr(
      0,
      scriptDirectory.replace(/[?#].*/, "").lastIndexOf("/") + 1
    );
  }
  {
    read_ = (url) => {
      var xhr = new XMLHttpRequest();
      xhr.open("GET", url, false);
      xhr.send(null);
      return xhr.responseText;
    };
    if (ENVIRONMENT_IS_WORKER) {
      readBinary = (url) => {
        var xhr = new XMLHttpRequest();
        xhr.open("GET", url, false);
        xhr.responseType = "arraybuffer";
        xhr.send(null);
        return new Uint8Array(xhr.response);
      };
    }
    readAsync = (url, onload, onerror) => {
      var xhr = new XMLHttpRequest();
      xhr.open("GET", url, true);
      xhr.responseType = "arraybuffer";
      xhr.onload = () => {
        if (xhr.status == 200 || (xhr.status == 0 && xhr.response)) {
          onload(xhr.response);
          return;
        }
        onerror();
      };
      xhr.onerror = onerror;
      xhr.send(null);
    };
  }
} else {
}
var out = Module["print"] || console.log.bind(console);
var err = Module["printErr"] || console.error.bind(console);
Object.assign(Module, moduleOverrides);
moduleOverrides = null;
if (Module["arguments"]) arguments_ = Module["arguments"];
if (Module["thisProgram"]) thisProgram = Module["thisProgram"];
if (Module["quit"]) quit_ = Module["quit"];
var wasmBinary;
if (Module["wasmBinary"]) wasmBinary = Module["wasmBinary"];
if (typeof WebAssembly != "object") {
  abort("no native wasm support detected");
}
var wasmMemory;
var ABORT = false;
var EXITSTATUS;
var HEAP8, HEAPU8, HEAP16, HEAPU16, HEAP32, HEAPU32, HEAPF32, HEAPF64;
function updateMemoryViews() {
  var b = wasmMemory.buffer;
  Module["HEAP8"] = HEAP8 = new Int8Array(b);
  Module["HEAP16"] = HEAP16 = new Int16Array(b);
  Module["HEAPU8"] = HEAPU8 = new Uint8Array(b);
  Module["HEAPU16"] = HEAPU16 = new Uint16Array(b);
  Module["HEAP32"] = HEAP32 = new Int32Array(b);
  Module["HEAPU32"] = HEAPU32 = new Uint32Array(b);
  Module["HEAPF32"] = HEAPF32 = new Float32Array(b);
  Module["HEAPF64"] = HEAPF64 = new Float64Array(b);
}
var __ATPRERUN__ = [];
var __ATINIT__ = [];
var __ATPOSTRUN__ = [];
var runtimeInitialized = false;
function preRun() {
  if (Module["preRun"]) {
    if (typeof Module["preRun"] == "function")
      Module["preRun"] = [Module["preRun"]];
    while (Module["preRun"].length) {
      addOnPreRun(Module["preRun"].shift());
    }
  }
  callRuntimeCallbacks(__ATPRERUN__);
}
function initRuntime() {
  runtimeInitialized = true;
  if (!Module["noFSInit"] && !FS.init.initialized) FS.init();
  FS.ignorePermissions = false;
  TTY.init();
  callRuntimeCallbacks(__ATINIT__);
}
function postRun() {
  if (Module["postRun"]) {
    if (typeof Module["postRun"] == "function")
      Module["postRun"] = [Module["postRun"]];
    while (Module["postRun"].length) {
      addOnPostRun(Module["postRun"].shift());
    }
  }
  callRuntimeCallbacks(__ATPOSTRUN__);
}
function addOnPreRun(cb) {
  __ATPRERUN__.unshift(cb);
}
function addOnInit(cb) {
  __ATINIT__.unshift(cb);
}
function addOnPostRun(cb) {
  __ATPOSTRUN__.unshift(cb);
}
var runDependencies = 0;
var runDependencyWatcher = null;
var dependenciesFulfilled = null;
function getUniqueRunDependency(id) {
  return id;
}
function addRunDependency(id) {
  runDependencies++;
  Module["monitorRunDependencies"]?.(runDependencies);
}
function removeRunDependency(id) {
  runDependencies--;
  Module["monitorRunDependencies"]?.(runDependencies);
  if (runDependencies == 0) {
    if (runDependencyWatcher !== null) {
      clearInterval(runDependencyWatcher);
      runDependencyWatcher = null;
    }
    if (dependenciesFulfilled) {
      var callback = dependenciesFulfilled;
      dependenciesFulfilled = null;
      callback();
    }
  }
}
function abort(what) {
  Module["onAbort"]?.(what);
  what = "Aborted(" + what + ")";
  err(what);
  ABORT = true;
  EXITSTATUS = 1;
  what += ". Build with -sASSERTIONS for more info.";
  var e = new WebAssembly.RuntimeError(what);
  throw e;
}
var dataURIPrefix = "data:application/octet-stream;base64,";
var isDataURI = (filename) => filename.startsWith(dataURIPrefix);
var isFileURI = (filename) => filename.startsWith("file://");
var wasmBinaryFile;
wasmBinaryFile = "sherpa-onnx-wasm-main-tts.wasm";
if (!isDataURI(wasmBinaryFile)) {
  wasmBinaryFile = locateFile(wasmBinaryFile);
}
function getBinarySync(file) {
  if (file == wasmBinaryFile && wasmBinary) {
    return new Uint8Array(wasmBinary);
  }
  if (readBinary) {
    return readBinary(file);
  }
  throw "both async and sync fetching of the wasm failed";
}
function getBinaryPromise(binaryFile) {
  if (!wasmBinary && (ENVIRONMENT_IS_WEB || ENVIRONMENT_IS_WORKER)) {
    if (typeof fetch == "function" && !isFileURI(binaryFile)) {
      return fetch(binaryFile, { credentials: "same-origin" })
        .then((response) => {
          if (!response["ok"]) {
            throw `failed to load wasm binary file at '${binaryFile}'`;
          }
          return response["arrayBuffer"]();
        })
        .catch(() => getBinarySync(binaryFile));
    } else if (readAsync) {
      return new Promise((resolve, reject) => {
        readAsync(
          binaryFile,
          (response) => resolve(new Uint8Array(response)),
          reject
        );
      });
    }
  }
  return Promise.resolve().then(() => getBinarySync(binaryFile));
}
function instantiateArrayBuffer(binaryFile, imports, receiver) {
  return getBinaryPromise(binaryFile)
    .then((binary) => WebAssembly.instantiate(binary, imports))
    .then((instance) => instance)
    .then(receiver, (reason) => {
      err(`failed to asynchronously prepare wasm: ${reason}`);
      abort(reason);
    });
}
function instantiateAsync(binary, binaryFile, imports, callback) {
  if (
    !binary &&
    typeof WebAssembly.instantiateStreaming == "function" &&
    !isDataURI(binaryFile) &&
    !isFileURI(binaryFile) &&
    !ENVIRONMENT_IS_NODE &&
    typeof fetch == "function"
  ) {
    return fetch(binaryFile, { credentials: "same-origin" }).then(
      (response) => {
        var result = WebAssembly.instantiateStreaming(response, imports);
        return result.then(callback, function (reason) {
          err(`wasm streaming compile failed: ${reason}`);
          err("falling back to ArrayBuffer instantiation");
          return instantiateArrayBuffer(binaryFile, imports, callback);
        });
      }
    );
  }
  return instantiateArrayBuffer(binaryFile, imports, callback);
}
function createWasm() {
  var info = { a: wasmImports };
  function receiveInstance(instance, module) {
    wasmExports = instance.exports;
    wasmMemory = wasmExports["L"];
    updateMemoryViews();
    addOnInit(wasmExports["M"]);
    removeRunDependency("wasm-instantiate");
    return wasmExports;
  }
  addRunDependency("wasm-instantiate");
  function receiveInstantiationResult(result) {
    receiveInstance(result["instance"]);
  }
  if (Module["instantiateWasm"]) {
    try {
      return Module["instantiateWasm"](info, receiveInstance);
    } catch (e) {
      err(`Module.instantiateWasm callback failed with error: ${e}`);
      return false;
    }
  }
  instantiateAsync(
    wasmBinary,
    wasmBinaryFile,
    info,
    receiveInstantiationResult
  );
  return {};
}
var tempDouble;
var tempI64;
var ASM_CONSTS = {
  1190960: ($0, $1, $2, $3) => {
    if (typeof Module == "undefined" || !Module.MountedFiles) {
      return 1;
    }
    let fileName = UTF8ToString($0 >>> 0);
    if (fileName.startsWith("./")) {
      fileName = fileName.substring(2);
    }
    const fileData = Module.MountedFiles.get(fileName);
    if (!fileData) {
      return 2;
    }
    const offset = $1 >>> 0;
    const length = $2 >>> 0;
    const buffer = $3 >>> 0;
    if (offset + length > fileData.byteLength) {
      return 3;
    }
    try {
      HEAPU8.set(fileData.subarray(offset, offset + length), buffer);
      return 0;
    } catch {
      return 4;
    }
  },
};
function ExitStatus(status) {
  this.name = "ExitStatus";
  this.message = `Program terminated with exit(${status})`;
  this.status = status;
}
var callRuntimeCallbacks = (callbacks) => {
  while (callbacks.length > 0) {
    callbacks.shift()(Module);
  }
};
function getValue(ptr, type = "i8") {
  if (type.endsWith("*")) type = "*";
  switch (type) {
    case "i1":
      return HEAP8[ptr >> 0];
    case "i8":
      return HEAP8[ptr >> 0];
    case "i16":
      return HEAP16[ptr >> 1];
    case "i32":
      return HEAP32[ptr >> 2];
    case "i64":
      abort("to do getValue(i64) use WASM_BIGINT");
    case "float":
      return HEAPF32[ptr >> 2];
    case "double":
      return HEAPF64[ptr >> 3];
    case "*":
      return HEAPU32[ptr >> 2];
    default:
      abort(`invalid type for getValue: ${type}`);
  }
}
var noExitRuntime = Module["noExitRuntime"] || true;
function setValue(ptr, value, type = "i8") {
  if (type.endsWith("*")) type = "*";
  switch (type) {
    case "i1":
      HEAP8[ptr >> 0] = value;
      break;
    case "i8":
      HEAP8[ptr >> 0] = value;
      break;
    case "i16":
      HEAP16[ptr >> 1] = value;
      break;
    case "i32":
      HEAP32[ptr >> 2] = value;
      break;
    case "i64":
      abort("to do setValue(i64) use WASM_BIGINT");
    case "float":
      HEAPF32[ptr >> 2] = value;
      break;
    case "double":
      HEAPF64[ptr >> 3] = value;
      break;
    case "*":
      HEAPU32[ptr >> 2] = value;
      break;
    default:
      abort(`invalid type for setValue: ${type}`);
  }
}
class ExceptionInfo {
  constructor(excPtr) {
    this.excPtr = excPtr;
    this.ptr = excPtr - 24;
  }
  set_type(type) {
    HEAPU32[(this.ptr + 4) >> 2] = type;
  }
  get_type() {
    return HEAPU32[(this.ptr + 4) >> 2];
  }
  set_destructor(destructor) {
    HEAPU32[(this.ptr + 8) >> 2] = destructor;
  }
  get_destructor() {
    return HEAPU32[(this.ptr + 8) >> 2];
  }
  set_caught(caught) {
    caught = caught ? 1 : 0;
    HEAP8[(this.ptr + 12) >> 0] = caught;
  }
  get_caught() {
    return HEAP8[(this.ptr + 12) >> 0] != 0;
  }
  set_rethrown(rethrown) {
    rethrown = rethrown ? 1 : 0;
    HEAP8[(this.ptr + 13) >> 0] = rethrown;
  }
  get_rethrown() {
    return HEAP8[(this.ptr + 13) >> 0] != 0;
  }
  init(type, destructor) {
    this.set_adjusted_ptr(0);
    this.set_type(type);
    this.set_destructor(destructor);
  }
  set_adjusted_ptr(adjustedPtr) {
    HEAPU32[(this.ptr + 16) >> 2] = adjustedPtr;
  }
  get_adjusted_ptr() {
    return HEAPU32[(this.ptr + 16) >> 2];
  }
  get_exception_ptr() {
    var isPointer = ___cxa_is_pointer_type(this.get_type());
    if (isPointer) {
      return HEAPU32[this.excPtr >> 2];
    }
    var adjusted = this.get_adjusted_ptr();
    if (adjusted !== 0) return adjusted;
    return this.excPtr;
  }
}
var exceptionLast = 0;
var uncaughtExceptionCount = 0;
var ___cxa_throw = (ptr, type, destructor) => {
  var info = new ExceptionInfo(ptr);
  info.init(type, destructor);
  exceptionLast = ptr;
  uncaughtExceptionCount++;
  throw exceptionLast;
};
var PATH = {
  isAbs: (path) => path.charAt(0) === "/",
  splitPath: (filename) => {
    var splitPathRe =
      /^(\/?|)([\s\S]*?)((?:\.{1,2}|[^\/]+?|)(\.[^.\/]*|))(?:[\/]*)$/;
    return splitPathRe.exec(filename).slice(1);
  },
  normalizeArray: (parts, allowAboveRoot) => {
    var up = 0;
    for (var i = parts.length - 1; i >= 0; i--) {
      var last = parts[i];
      if (last === ".") {
        parts.splice(i, 1);
      } else if (last === "..") {
        parts.splice(i, 1);
        up++;
      } else if (up) {
        parts.splice(i, 1);
        up--;
      }
    }
    if (allowAboveRoot) {
      for (; up; up--) {
        parts.unshift("..");
      }
    }
    return parts;
  },
  normalize: (path) => {
    var isAbsolute = PATH.isAbs(path),
      trailingSlash = path.substr(-1) === "/";
    path = PATH.normalizeArray(
      path.split("/").filter((p) => !!p),
      !isAbsolute
    ).join("/");
    if (!path && !isAbsolute) {
      path = ".";
    }
    if (path && trailingSlash) {
      path += "/";
    }
    return (isAbsolute ? "/" : "") + path;
  },
  dirname: (path) => {
    var result = PATH.splitPath(path),
      root = result[0],
      dir = result[1];
    if (!root && !dir) {
      return ".";
    }
    if (dir) {
      dir = dir.substr(0, dir.length - 1);
    }
    return root + dir;
  },
  basename: (path) => {
    if (path === "/") return "/";
    path = PATH.normalize(path);
    path = path.replace(/\/$/, "");
    var lastSlash = path.lastIndexOf("/");
    if (lastSlash === -1) return path;
    return path.substr(lastSlash + 1);
  },
  join: function () {
    var paths = Array.prototype.slice.call(arguments);
    return PATH.normalize(paths.join("/"));
  },
  join2: (l, r) => PATH.normalize(l + "/" + r),
};
var initRandomFill = () => {
  if (
    typeof crypto == "object" &&
    typeof crypto["getRandomValues"] == "function"
  ) {
    return (view) => crypto.getRandomValues(view);
  } else if (ENVIRONMENT_IS_NODE) {
    try {
      var crypto_module = require("crypto");
      var randomFillSync = crypto_module["randomFillSync"];
      if (randomFillSync) {
        return (view) => crypto_module["randomFillSync"](view);
      }
      var randomBytes = crypto_module["randomBytes"];
      return (view) => (view.set(randomBytes(view.byteLength)), view);
    } catch (e) {}
  }
  abort("initRandomDevice");
};
var randomFill = (view) => (randomFill = initRandomFill())(view);
var PATH_FS = {
  resolve: function () {
    var resolvedPath = "",
      resolvedAbsolute = false;
    for (var i = arguments.length - 1; i >= -1 && !resolvedAbsolute; i--) {
      var path = i >= 0 ? arguments[i] : FS.cwd();
      if (typeof path != "string") {
        throw new TypeError("Arguments to path.resolve must be strings");
      } else if (!path) {
        return "";
      }
      resolvedPath = path + "/" + resolvedPath;
      resolvedAbsolute = PATH.isAbs(path);
    }
    resolvedPath = PATH.normalizeArray(
      resolvedPath.split("/").filter((p) => !!p),
      !resolvedAbsolute
    ).join("/");
    return (resolvedAbsolute ? "/" : "") + resolvedPath || ".";
  },
  relative: (from, to) => {
    from = PATH_FS.resolve(from).substr(1);
    to = PATH_FS.resolve(to).substr(1);
    function trim(arr) {
      var start = 0;
      for (; start < arr.length; start++) {
        if (arr[start] !== "") break;
      }
      var end = arr.length - 1;
      for (; end >= 0; end--) {
        if (arr[end] !== "") break;
      }
      if (start > end) return [];
      return arr.slice(start, end - start + 1);
    }
    var fromParts = trim(from.split("/"));
    var toParts = trim(to.split("/"));
    var length = Math.min(fromParts.length, toParts.length);
    var samePartsLength = length;
    for (var i = 0; i < length; i++) {
      if (fromParts[i] !== toParts[i]) {
        samePartsLength = i;
        break;
      }
    }
    var outputParts = [];
    for (var i = samePartsLength; i < fromParts.length; i++) {
      outputParts.push("..");
    }
    outputParts = outputParts.concat(toParts.slice(samePartsLength));
    return outputParts.join("/");
  },
};
var UTF8Decoder =
  typeof TextDecoder != "undefined" ? new TextDecoder("utf8") : undefined;
var UTF8ArrayToString = (heapOrArray, idx, maxBytesToRead) => {
  var endIdx = idx + maxBytesToRead;
  var endPtr = idx;
  while (heapOrArray[endPtr] && !(endPtr >= endIdx)) ++endPtr;
  if (endPtr - idx > 16 && heapOrArray.buffer && UTF8Decoder) {
    return UTF8Decoder.decode(heapOrArray.subarray(idx, endPtr));
  }
  var str = "";
  while (idx < endPtr) {
    var u0 = heapOrArray[idx++];
    if (!(u0 & 128)) {
      str += String.fromCharCode(u0);
      continue;
    }
    var u1 = heapOrArray[idx++] & 63;
    if ((u0 & 224) == 192) {
      str += String.fromCharCode(((u0 & 31) << 6) | u1);
      continue;
    }
    var u2 = heapOrArray[idx++] & 63;
    if ((u0 & 240) == 224) {
      u0 = ((u0 & 15) << 12) | (u1 << 6) | u2;
    } else {
      u0 =
        ((u0 & 7) << 18) | (u1 << 12) | (u2 << 6) | (heapOrArray[idx++] & 63);
    }
    if (u0 < 65536) {
      str += String.fromCharCode(u0);
    } else {
      var ch = u0 - 65536;
      str += String.fromCharCode(55296 | (ch >> 10), 56320 | (ch & 1023));
    }
  }
  return str;
};
var FS_stdin_getChar_buffer = [];
var lengthBytesUTF8 = (str) => {
  var len = 0;
  for (var i = 0; i < str.length; ++i) {
    var c = str.charCodeAt(i);
    if (c <= 127) {
      len++;
    } else if (c <= 2047) {
      len += 2;
    } else if (c >= 55296 && c <= 57343) {
      len += 4;
      ++i;
    } else {
      len += 3;
    }
  }
  return len;
};
var stringToUTF8Array = (str, heap, outIdx, maxBytesToWrite) => {
  if (!(maxBytesToWrite > 0)) return 0;
  var startIdx = outIdx;
  var endIdx = outIdx + maxBytesToWrite - 1;
  for (var i = 0; i < str.length; ++i) {
    var u = str.charCodeAt(i);
    if (u >= 55296 && u <= 57343) {
      var u1 = str.charCodeAt(++i);
      u = (65536 + ((u & 1023) << 10)) | (u1 & 1023);
    }
    if (u <= 127) {
      if (outIdx >= endIdx) break;
      heap[outIdx++] = u;
    } else if (u <= 2047) {
      if (outIdx + 1 >= endIdx) break;
      heap[outIdx++] = 192 | (u >> 6);
      heap[outIdx++] = 128 | (u & 63);
    } else if (u <= 65535) {
      if (outIdx + 2 >= endIdx) break;
      heap[outIdx++] = 224 | (u >> 12);
      heap[outIdx++] = 128 | ((u >> 6) & 63);
      heap[outIdx++] = 128 | (u & 63);
    } else {
      if (outIdx + 3 >= endIdx) break;
      heap[outIdx++] = 240 | (u >> 18);
      heap[outIdx++] = 128 | ((u >> 12) & 63);
      heap[outIdx++] = 128 | ((u >> 6) & 63);
      heap[outIdx++] = 128 | (u & 63);
    }
  }
  heap[outIdx] = 0;
  return outIdx - startIdx;
};
function intArrayFromString(stringy, dontAddNull, length) {
  var len = length > 0 ? length : lengthBytesUTF8(stringy) + 1;
  var u8array = new Array(len);
  var numBytesWritten = stringToUTF8Array(stringy, u8array, 0, u8array.length);
  if (dontAddNull) u8array.length = numBytesWritten;
  return u8array;
}
var FS_stdin_getChar = () => {
  if (!FS_stdin_getChar_buffer.length) {
    var result = null;
    if (ENVIRONMENT_IS_NODE) {
      var BUFSIZE = 256;
      var buf = Buffer.alloc(BUFSIZE);
      var bytesRead = 0;
      var fd = process.stdin.fd;
      try {
        bytesRead = fs.readSync(fd, buf);
      } catch (e) {
        if (e.toString().includes("EOF")) bytesRead = 0;
        else throw e;
      }
      if (bytesRead > 0) {
        result = buf.slice(0, bytesRead).toString("utf-8");
      } else {
        result = null;
      }
    } else if (
      typeof window != "undefined" &&
      typeof window.prompt == "function"
    ) {
      result = window.prompt("Input: ");
      if (result !== null) {
        result += "\n";
      }
    } else if (typeof readline == "function") {
      result = readline();
      if (result !== null) {
        result += "\n";
      }
    }
    if (!result) {
      return null;
    }
    FS_stdin_getChar_buffer = intArrayFromString(result, true);
  }
  return FS_stdin_getChar_buffer.shift();
};
var TTY = {
  ttys: [],
  init() {},
  shutdown() {},
  register(dev, ops) {
    TTY.ttys[dev] = { input: [], output: [], ops: ops };
    FS.registerDevice(dev, TTY.stream_ops);
  },
  stream_ops: {
    open(stream) {
      var tty = TTY.ttys[stream.node.rdev];
      if (!tty) {
        throw new FS.ErrnoError(43);
      }
      stream.tty = tty;
      stream.seekable = false;
    },
    close(stream) {
      stream.tty.ops.fsync(stream.tty);
    },
    fsync(stream) {
      stream.tty.ops.fsync(stream.tty);
    },
    read(stream, buffer, offset, length, pos) {
      if (!stream.tty || !stream.tty.ops.get_char) {
        throw new FS.ErrnoError(60);
      }
      var bytesRead = 0;
      for (var i = 0; i < length; i++) {
        var result;
        try {
          result = stream.tty.ops.get_char(stream.tty);
        } catch (e) {
          throw new FS.ErrnoError(29);
        }
        if (result === undefined && bytesRead === 0) {
          throw new FS.ErrnoError(6);
        }
        if (result === null || result === undefined) break;
        bytesRead++;
        buffer[offset + i] = result;
      }
      if (bytesRead) {
        stream.node.timestamp = Date.now();
      }
      return bytesRead;
    },
    write(stream, buffer, offset, length, pos) {
      if (!stream.tty || !stream.tty.ops.put_char) {
        throw new FS.ErrnoError(60);
      }
      try {
        for (var i = 0; i < length; i++) {
          stream.tty.ops.put_char(stream.tty, buffer[offset + i]);
        }
      } catch (e) {
        throw new FS.ErrnoError(29);
      }
      if (length) {
        stream.node.timestamp = Date.now();
      }
      return i;
    },
  },
  default_tty_ops: {
    get_char(tty) {
      return FS_stdin_getChar();
    },
    put_char(tty, val) {
      if (val === null || val === 10) {
        out(UTF8ArrayToString(tty.output, 0));
        tty.output = [];
      } else {
        if (val != 0) tty.output.push(val);
      }
    },
    fsync(tty) {
      if (tty.output && tty.output.length > 0) {
        out(UTF8ArrayToString(tty.output, 0));
        tty.output = [];
      }
    },
    ioctl_tcgets(tty) {
      return {
        c_iflag: 25856,
        c_oflag: 5,
        c_cflag: 191,
        c_lflag: 35387,
        c_cc: [
          3, 28, 127, 21, 4, 0, 1, 0, 17, 19, 26, 0, 18, 15, 23, 22, 0, 0, 0, 0,
          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        ],
      };
    },
    ioctl_tcsets(tty, optional_actions, data) {
      return 0;
    },
    ioctl_tiocgwinsz(tty) {
      return [24, 80];
    },
  },
  default_tty1_ops: {
    put_char(tty, val) {
      if (val === null || val === 10) {
        err(UTF8ArrayToString(tty.output, 0));
        tty.output = [];
      } else {
        if (val != 0) tty.output.push(val);
      }
    },
    fsync(tty) {
      if (tty.output && tty.output.length > 0) {
        err(UTF8ArrayToString(tty.output, 0));
        tty.output = [];
      }
    },
  },
};
var zeroMemory = (address, size) => {
  HEAPU8.fill(0, address, address + size);
  return address;
};
var alignMemory = (size, alignment) => Math.ceil(size / alignment) * alignment;
var mmapAlloc = (size) => {
  size = alignMemory(size, 65536);
  var ptr = _emscripten_builtin_memalign(65536, size);
  if (!ptr) return 0;
  return zeroMemory(ptr, size);
};
var MEMFS = {
  ops_table: null,
  mount(mount) {
    return MEMFS.createNode(null, "/", 16384 | 511, 0);
  },
  createNode(parent, name, mode, dev) {
    if (FS.isBlkdev(mode) || FS.isFIFO(mode)) {
      throw new FS.ErrnoError(63);
    }
    MEMFS.ops_table ||= {
      dir: {
        node: {
          getattr: MEMFS.node_ops.getattr,
          setattr: MEMFS.node_ops.setattr,
          lookup: MEMFS.node_ops.lookup,
          mknod: MEMFS.node_ops.mknod,
          rename: MEMFS.node_ops.rename,
          unlink: MEMFS.node_ops.unlink,
          rmdir: MEMFS.node_ops.rmdir,
          readdir: MEMFS.node_ops.readdir,
          symlink: MEMFS.node_ops.symlink,
        },
        stream: { llseek: MEMFS.stream_ops.llseek },
      },
      file: {
        node: {
          getattr: MEMFS.node_ops.getattr,
          setattr: MEMFS.node_ops.setattr,
        },
        stream: {
          llseek: MEMFS.stream_ops.llseek,
          read: MEMFS.stream_ops.read,
          write: MEMFS.stream_ops.write,
          allocate: MEMFS.stream_ops.allocate,
          mmap: MEMFS.stream_ops.mmap,
          msync: MEMFS.stream_ops.msync,
        },
      },
      link: {
        node: {
          getattr: MEMFS.node_ops.getattr,
          setattr: MEMFS.node_ops.setattr,
          readlink: MEMFS.node_ops.readlink,
        },
        stream: {},
      },
      chrdev: {
        node: {
          getattr: MEMFS.node_ops.getattr,
          setattr: MEMFS.node_ops.setattr,
        },
        stream: FS.chrdev_stream_ops,
      },
    };
    var node = FS.createNode(parent, name, mode, dev);
    if (FS.isDir(node.mode)) {
      node.node_ops = MEMFS.ops_table.dir.node;
      node.stream_ops = MEMFS.ops_table.dir.stream;
      node.contents = {};
    } else if (FS.isFile(node.mode)) {
      node.node_ops = MEMFS.ops_table.file.node;
      node.stream_ops = MEMFS.ops_table.file.stream;
      node.usedBytes = 0;
      node.contents = null;
    } else if (FS.isLink(node.mode)) {
      node.node_ops = MEMFS.ops_table.link.node;
      node.stream_ops = MEMFS.ops_table.link.stream;
    } else if (FS.isChrdev(node.mode)) {
      node.node_ops = MEMFS.ops_table.chrdev.node;
      node.stream_ops = MEMFS.ops_table.chrdev.stream;
    }
    node.timestamp = Date.now();
    if (parent) {
      parent.contents[name] = node;
      parent.timestamp = node.timestamp;
    }
    return node;
  },
  getFileDataAsTypedArray(node) {
    if (!node.contents) return new Uint8Array(0);
    if (node.contents.subarray)
      return node.contents.subarray(0, node.usedBytes);
    return new Uint8Array(node.contents);
  },
  expandFileStorage(node, newCapacity) {
    var prevCapacity = node.contents ? node.contents.length : 0;
    if (prevCapacity >= newCapacity) return;
    var CAPACITY_DOUBLING_MAX = 1024 * 1024;
    newCapacity = Math.max(
      newCapacity,
      (prevCapacity * (prevCapacity < CAPACITY_DOUBLING_MAX ? 2 : 1.125)) >>> 0
    );
    if (prevCapacity != 0) newCapacity = Math.max(newCapacity, 256);
    var oldContents = node.contents;
    node.contents = new Uint8Array(newCapacity);
    if (node.usedBytes > 0)
      node.contents.set(oldContents.subarray(0, node.usedBytes), 0);
  },
  resizeFileStorage(node, newSize) {
    if (node.usedBytes == newSize) return;
    if (newSize == 0) {
      node.contents = null;
      node.usedBytes = 0;
    } else {
      var oldContents = node.contents;
      node.contents = new Uint8Array(newSize);
      if (oldContents) {
        node.contents.set(
          oldContents.subarray(0, Math.min(newSize, node.usedBytes))
        );
      }
      node.usedBytes = newSize;
    }
  },
  node_ops: {
    getattr(node) {
      var attr = {};
      attr.dev = FS.isChrdev(node.mode) ? node.id : 1;
      attr.ino = node.id;
      attr.mode = node.mode;
      attr.nlink = 1;
      attr.uid = 0;
      attr.gid = 0;
      attr.rdev = node.rdev;
      if (FS.isDir(node.mode)) {
        attr.size = 4096;
      } else if (FS.isFile(node.mode)) {
        attr.size = node.usedBytes;
      } else if (FS.isLink(node.mode)) {
        attr.size = node.link.length;
      } else {
        attr.size = 0;
      }
      attr.atime = new Date(node.timestamp);
      attr.mtime = new Date(node.timestamp);
      attr.ctime = new Date(node.timestamp);
      attr.blksize = 4096;
      attr.blocks = Math.ceil(attr.size / attr.blksize);
      return attr;
    },
    setattr(node, attr) {
      if (attr.mode !== undefined) {
        node.mode = attr.mode;
      }
      if (attr.timestamp !== undefined) {
        node.timestamp = attr.timestamp;
      }
      if (attr.size !== undefined) {
        MEMFS.resizeFileStorage(node, attr.size);
      }
    },
    lookup(parent, name) {
      throw FS.genericErrors[44];
    },
    mknod(parent, name, mode, dev) {
      return MEMFS.createNode(parent, name, mode, dev);
    },
    rename(old_node, new_dir, new_name) {
      if (FS.isDir(old_node.mode)) {
        var new_node;
        try {
          new_node = FS.lookupNode(new_dir, new_name);
        } catch (e) {}
        if (new_node) {
          for (var i in new_node.contents) {
            throw new FS.ErrnoError(55);
          }
        }
      }
      delete old_node.parent.contents[old_node.name];
      old_node.parent.timestamp = Date.now();
      old_node.name = new_name;
      new_dir.contents[new_name] = old_node;
      new_dir.timestamp = old_node.parent.timestamp;
      old_node.parent = new_dir;
    },
    unlink(parent, name) {
      delete parent.contents[name];
      parent.timestamp = Date.now();
    },
    rmdir(parent, name) {
      var node = FS.lookupNode(parent, name);
      for (var i in node.contents) {
        throw new FS.ErrnoError(55);
      }
      delete parent.contents[name];
      parent.timestamp = Date.now();
    },
    readdir(node) {
      var entries = [".", ".."];
      for (var key of Object.keys(node.contents)) {
        entries.push(key);
      }
      return entries;
    },
    symlink(parent, newname, oldpath) {
      var node = MEMFS.createNode(parent, newname, 511 | 40960, 0);
      node.link = oldpath;
      return node;
    },
    readlink(node) {
      if (!FS.isLink(node.mode)) {
        throw new FS.ErrnoError(28);
      }
      return node.link;
    },
  },
  stream_ops: {
    read(stream, buffer, offset, length, position) {
      var contents = stream.node.contents;
      if (position >= stream.node.usedBytes) return 0;
      var size = Math.min(stream.node.usedBytes - position, length);
      if (size > 8 && contents.subarray) {
        buffer.set(contents.subarray(position, position + size), offset);
      } else {
        for (var i = 0; i < size; i++)
          buffer[offset + i] = contents[position + i];
      }
      return size;
    },
    write(stream, buffer, offset, length, position, canOwn) {
      if (buffer.buffer === HEAP8.buffer) {
        canOwn = false;
      }
      if (!length) return 0;
      var node = stream.node;
      node.timestamp = Date.now();
      if (buffer.subarray && (!node.contents || node.contents.subarray)) {
        if (canOwn) {
          node.contents = buffer.subarray(offset, offset + length);
          node.usedBytes = length;
          return length;
        } else if (node.usedBytes === 0 && position === 0) {
          node.contents = buffer.slice(offset, offset + length);
          node.usedBytes = length;
          return length;
        } else if (position + length <= node.usedBytes) {
          node.contents.set(buffer.subarray(offset, offset + length), position);
          return length;
        }
      }
      MEMFS.expandFileStorage(node, position + length);
      if (node.contents.subarray && buffer.subarray) {
        node.contents.set(buffer.subarray(offset, offset + length), position);
      } else {
        for (var i = 0; i < length; i++) {
          node.contents[position + i] = buffer[offset + i];
        }
      }
      node.usedBytes = Math.max(node.usedBytes, position + length);
      return length;
    },
    llseek(stream, offset, whence) {
      var position = offset;
      if (whence === 1) {
        position += stream.position;
      } else if (whence === 2) {
        if (FS.isFile(stream.node.mode)) {
          position += stream.node.usedBytes;
        }
      }
      if (position < 0) {
        throw new FS.ErrnoError(28);
      }
      return position;
    },
    allocate(stream, offset, length) {
      MEMFS.expandFileStorage(stream.node, offset + length);
      stream.node.usedBytes = Math.max(stream.node.usedBytes, offset + length);
    },
    mmap(stream, length, position, prot, flags) {
      if (!FS.isFile(stream.node.mode)) {
        throw new FS.ErrnoError(43);
      }
      var ptr;
      var allocated;
      var contents = stream.node.contents;
      if (!(flags & 2) && contents.buffer === HEAP8.buffer) {
        allocated = false;
        ptr = contents.byteOffset;
      } else {
        if (position > 0 || position + length < contents.length) {
          if (contents.subarray) {
            contents = contents.subarray(position, position + length);
          } else {
            contents = Array.prototype.slice.call(
              contents,
              position,
              position + length
            );
          }
        }
        allocated = true;
        ptr = mmapAlloc(length);
        if (!ptr) {
          throw new FS.ErrnoError(48);
        }
        HEAP8.set(contents, ptr);
      }
      return { ptr: ptr, allocated: allocated };
    },
    msync(stream, buffer, offset, length, mmapFlags) {
      MEMFS.stream_ops.write(stream, buffer, 0, length, offset, false);
      return 0;
    },
  },
};
var asyncLoad = (url, onload, onerror, noRunDep) => {
  var dep = !noRunDep ? getUniqueRunDependency(`al ${url}`) : "";
  readAsync(
    url,
    (arrayBuffer) => {
      onload(new Uint8Array(arrayBuffer));
      if (dep) removeRunDependency(dep);
    },
    (event) => {
      if (onerror) {
        onerror();
      } else {
        throw `Loading data file "${url}" failed.`;
      }
    }
  );
  if (dep) addRunDependency(dep);
};
var FS_createDataFile = (parent, name, fileData, canRead, canWrite, canOwn) => {
  FS.createDataFile(parent, name, fileData, canRead, canWrite, canOwn);
};
var preloadPlugins = Module["preloadPlugins"] || [];
var FS_handledByPreloadPlugin = (byteArray, fullname, finish, onerror) => {
  if (typeof Browser != "undefined") Browser.init();
  var handled = false;
  preloadPlugins.forEach((plugin) => {
    if (handled) return;
    if (plugin["canHandle"](fullname)) {
      plugin["handle"](byteArray, fullname, finish, onerror);
      handled = true;
    }
  });
  return handled;
};
var FS_createPreloadedFile = (
  parent,
  name,
  url,
  canRead,
  canWrite,
  onload,
  onerror,
  dontCreateFile,
  canOwn,
  preFinish
) => {
  var fullname = name ? PATH_FS.resolve(PATH.join2(parent, name)) : parent;
  var dep = getUniqueRunDependency(`cp ${fullname}`);
  function processData(byteArray) {
    function finish(byteArray) {
      preFinish?.();
      if (!dontCreateFile) {
        FS_createDataFile(parent, name, byteArray, canRead, canWrite, canOwn);
      }
      onload?.();
      removeRunDependency(dep);
    }
    if (
      FS_handledByPreloadPlugin(byteArray, fullname, finish, () => {
        onerror?.();
        removeRunDependency(dep);
      })
    ) {
      return;
    }
    finish(byteArray);
  }
  addRunDependency(dep);
  if (typeof url == "string") {
    asyncLoad(url, processData, onerror);
  } else {
    processData(url);
  }
};
var FS_modeStringToFlags = (str) => {
  var flagModes = {
    r: 0,
    "r+": 2,
    w: 512 | 64 | 1,
    "w+": 512 | 64 | 2,
    a: 1024 | 64 | 1,
    "a+": 1024 | 64 | 2,
  };
  var flags = flagModes[str];
  if (typeof flags == "undefined") {
    throw new Error(`Unknown file open mode: ${str}`);
  }
  return flags;
};
var FS_getMode = (canRead, canWrite) => {
  var mode = 0;
  if (canRead) mode |= 292 | 73;
  if (canWrite) mode |= 146;
  return mode;
};
var FS = {
  root: null,
  mounts: [],
  devices: {},
  streams: [],
  nextInode: 1,
  nameTable: null,
  currentPath: "/",
  initialized: false,
  ignorePermissions: true,
  ErrnoError: class {
    constructor(errno) {
      this.name = "ErrnoError";
      this.errno = errno;
    }
  },
  genericErrors: {},
  filesystems: null,
  syncFSRequests: 0,
  lookupPath(path, opts = {}) {
    path = PATH_FS.resolve(path);
    if (!path) return { path: "", node: null };
    var defaults = { follow_mount: true, recurse_count: 0 };
    opts = Object.assign(defaults, opts);
    if (opts.recurse_count > 8) {
      throw new FS.ErrnoError(32);
    }
    var parts = path.split("/").filter((p) => !!p);
    var current = FS.root;
    var current_path = "/";
    for (var i = 0; i < parts.length; i++) {
      var islast = i === parts.length - 1;
      if (islast && opts.parent) {
        break;
      }
      current = FS.lookupNode(current, parts[i]);
      current_path = PATH.join2(current_path, parts[i]);
      if (FS.isMountpoint(current)) {
        if (!islast || (islast && opts.follow_mount)) {
          current = current.mounted.root;
        }
      }
      if (!islast || opts.follow) {
        var count = 0;
        while (FS.isLink(current.mode)) {
          var link = FS.readlink(current_path);
          current_path = PATH_FS.resolve(PATH.dirname(current_path), link);
          var lookup = FS.lookupPath(current_path, {
            recurse_count: opts.recurse_count + 1,
          });
          current = lookup.node;
          if (count++ > 40) {
            throw new FS.ErrnoError(32);
          }
        }
      }
    }
    return { path: current_path, node: current };
  },
  getPath(node) {
    var path;
    while (true) {
      if (FS.isRoot(node)) {
        var mount = node.mount.mountpoint;
        if (!path) return mount;
        return mount[mount.length - 1] !== "/"
          ? `${mount}/${path}`
          : mount + path;
      }
      path = path ? `${node.name}/${path}` : node.name;
      node = node.parent;
    }
  },
  hashName(parentid, name) {
    var hash = 0;
    for (var i = 0; i < name.length; i++) {
      hash = ((hash << 5) - hash + name.charCodeAt(i)) | 0;
    }
    return ((parentid + hash) >>> 0) % FS.nameTable.length;
  },
  hashAddNode(node) {
    var hash = FS.hashName(node.parent.id, node.name);
    node.name_next = FS.nameTable[hash];
    FS.nameTable[hash] = node;
  },
  hashRemoveNode(node) {
    var hash = FS.hashName(node.parent.id, node.name);
    if (FS.nameTable[hash] === node) {
      FS.nameTable[hash] = node.name_next;
    } else {
      var current = FS.nameTable[hash];
      while (current) {
        if (current.name_next === node) {
          current.name_next = node.name_next;
          break;
        }
        current = current.name_next;
      }
    }
  },
  lookupNode(parent, name) {
    var errCode = FS.mayLookup(parent);
    if (errCode) {
      throw new FS.ErrnoError(errCode);
    }
    var hash = FS.hashName(parent.id, name);
    for (var node = FS.nameTable[hash]; node; node = node.name_next) {
      var nodeName = node.name;
      if (node.parent.id === parent.id && nodeName === name) {
        return node;
      }
    }
    return FS.lookup(parent, name);
  },
  createNode(parent, name, mode, rdev) {
    var node = new FS.FSNode(parent, name, mode, rdev);
    FS.hashAddNode(node);
    return node;
  },
  destroyNode(node) {
    FS.hashRemoveNode(node);
  },
  isRoot(node) {
    return node === node.parent;
  },
  isMountpoint(node) {
    return !!node.mounted;
  },
  isFile(mode) {
    return (mode & 61440) === 32768;
  },
  isDir(mode) {
    return (mode & 61440) === 16384;
  },
  isLink(mode) {
    return (mode & 61440) === 40960;
  },
  isChrdev(mode) {
    return (mode & 61440) === 8192;
  },
  isBlkdev(mode) {
    return (mode & 61440) === 24576;
  },
  isFIFO(mode) {
    return (mode & 61440) === 4096;
  },
  isSocket(mode) {
    return (mode & 49152) === 49152;
  },
  flagsToPermissionString(flag) {
    var perms = ["r", "w", "rw"][flag & 3];
    if (flag & 512) {
      perms += "w";
    }
    return perms;
  },
  nodePermissions(node, perms) {
    if (FS.ignorePermissions) {
      return 0;
    }
    if (perms.includes("r") && !(node.mode & 292)) {
      return 2;
    } else if (perms.includes("w") && !(node.mode & 146)) {
      return 2;
    } else if (perms.includes("x") && !(node.mode & 73)) {
      return 2;
    }
    return 0;
  },
  mayLookup(dir) {
    if (!FS.isDir(dir.mode)) return 54;
    var errCode = FS.nodePermissions(dir, "x");
    if (errCode) return errCode;
    if (!dir.node_ops.lookup) return 2;
    return 0;
  },
  mayCreate(dir, name) {
    try {
      var node = FS.lookupNode(dir, name);
      return 20;
    } catch (e) {}
    return FS.nodePermissions(dir, "wx");
  },
  mayDelete(dir, name, isdir) {
    var node;
    try {
      node = FS.lookupNode(dir, name);
    } catch (e) {
      return e.errno;
    }
    var errCode = FS.nodePermissions(dir, "wx");
    if (errCode) {
      return errCode;
    }
    if (isdir) {
      if (!FS.isDir(node.mode)) {
        return 54;
      }
      if (FS.isRoot(node) || FS.getPath(node) === FS.cwd()) {
        return 10;
      }
    } else {
      if (FS.isDir(node.mode)) {
        return 31;
      }
    }
    return 0;
  },
  mayOpen(node, flags) {
    if (!node) {
      return 44;
    }
    if (FS.isLink(node.mode)) {
      return 32;
    } else if (FS.isDir(node.mode)) {
      if (FS.flagsToPermissionString(flags) !== "r" || flags & 512) {
        return 31;
      }
    }
    return FS.nodePermissions(node, FS.flagsToPermissionString(flags));
  },
  MAX_OPEN_FDS: 4096,
  nextfd() {
    for (var fd = 0; fd <= FS.MAX_OPEN_FDS; fd++) {
      if (!FS.streams[fd]) {
        return fd;
      }
    }
    throw new FS.ErrnoError(33);
  },
  getStreamChecked(fd) {
    var stream = FS.getStream(fd);
    if (!stream) {
      throw new FS.ErrnoError(8);
    }
    return stream;
  },
  getStream: (fd) => FS.streams[fd],
  createStream(stream, fd = -1) {
    if (!FS.FSStream) {
      FS.FSStream = function () {
        this.shared = {};
      };
      FS.FSStream.prototype = {};
      Object.defineProperties(FS.FSStream.prototype, {
        object: {
          get() {
            return this.node;
          },
          set(val) {
            this.node = val;
          },
        },
        isRead: {
          get() {
            return (this.flags & 2097155) !== 1;
          },
        },
        isWrite: {
          get() {
            return (this.flags & 2097155) !== 0;
          },
        },
        isAppend: {
          get() {
            return this.flags & 1024;
          },
        },
        flags: {
          get() {
            return this.shared.flags;
          },
          set(val) {
            this.shared.flags = val;
          },
        },
        position: {
          get() {
            return this.shared.position;
          },
          set(val) {
            this.shared.position = val;
          },
        },
      });
    }
    stream = Object.assign(new FS.FSStream(), stream);
    if (fd == -1) {
      fd = FS.nextfd();
    }
    stream.fd = fd;
    FS.streams[fd] = stream;
    return stream;
  },
  closeStream(fd) {
    FS.streams[fd] = null;
  },
  chrdev_stream_ops: {
    open(stream) {
      var device = FS.getDevice(stream.node.rdev);
      stream.stream_ops = device.stream_ops;
      stream.stream_ops.open?.(stream);
    },
    llseek() {
      throw new FS.ErrnoError(70);
    },
  },
  major: (dev) => dev >> 8,
  minor: (dev) => dev & 255,
  makedev: (ma, mi) => (ma << 8) | mi,
  registerDevice(dev, ops) {
    FS.devices[dev] = { stream_ops: ops };
  },
  getDevice: (dev) => FS.devices[dev],
  getMounts(mount) {
    var mounts = [];
    var check = [mount];
    while (check.length) {
      var m = check.pop();
      mounts.push(m);
      check.push.apply(check, m.mounts);
    }
    return mounts;
  },
  syncfs(populate, callback) {
    if (typeof populate == "function") {
      callback = populate;
      populate = false;
    }
    FS.syncFSRequests++;
    if (FS.syncFSRequests > 1) {
      err(
        `warning: ${FS.syncFSRequests} FS.syncfs operations in flight at once, probably just doing extra work`
      );
    }
    var mounts = FS.getMounts(FS.root.mount);
    var completed = 0;
    function doCallback(errCode) {
      FS.syncFSRequests--;
      return callback(errCode);
    }
    function done(errCode) {
      if (errCode) {
        if (!done.errored) {
          done.errored = true;
          return doCallback(errCode);
        }
        return;
      }
      if (++completed >= mounts.length) {
        doCallback(null);
      }
    }
    mounts.forEach((mount) => {
      if (!mount.type.syncfs) {
        return done(null);
      }
      mount.type.syncfs(mount, populate, done);
    });
  },
  mount(type, opts, mountpoint) {
    var root = mountpoint === "/";
    var pseudo = !mountpoint;
    var node;
    if (root && FS.root) {
      throw new FS.ErrnoError(10);
    } else if (!root && !pseudo) {
      var lookup = FS.lookupPath(mountpoint, { follow_mount: false });
      mountpoint = lookup.path;
      node = lookup.node;
      if (FS.isMountpoint(node)) {
        throw new FS.ErrnoError(10);
      }
      if (!FS.isDir(node.mode)) {
        throw new FS.ErrnoError(54);
      }
    }
    var mount = { type: type, opts: opts, mountpoint: mountpoint, mounts: [] };
    var mountRoot = type.mount(mount);
    mountRoot.mount = mount;
    mount.root = mountRoot;
    if (root) {
      FS.root = mountRoot;
    } else if (node) {
      node.mounted = mount;
      if (node.mount) {
        node.mount.mounts.push(mount);
      }
    }
    return mountRoot;
  },
  unmount(mountpoint) {
    var lookup = FS.lookupPath(mountpoint, { follow_mount: false });
    if (!FS.isMountpoint(lookup.node)) {
      throw new FS.ErrnoError(28);
    }
    var node = lookup.node;
    var mount = node.mounted;
    var mounts = FS.getMounts(mount);
    Object.keys(FS.nameTable).forEach((hash) => {
      var current = FS.nameTable[hash];
      while (current) {
        var next = current.name_next;
        if (mounts.includes(current.mount)) {
          FS.destroyNode(current);
        }
        current = next;
      }
    });
    node.mounted = null;
    var idx = node.mount.mounts.indexOf(mount);
    node.mount.mounts.splice(idx, 1);
  },
  lookup(parent, name) {
    return parent.node_ops.lookup(parent, name);
  },
  mknod(path, mode, dev) {
    var lookup = FS.lookupPath(path, { parent: true });
    var parent = lookup.node;
    var name = PATH.basename(path);
    if (!name || name === "." || name === "..") {
      throw new FS.ErrnoError(28);
    }
    var errCode = FS.mayCreate(parent, name);
    if (errCode) {
      throw new FS.ErrnoError(errCode);
    }
    if (!parent.node_ops.mknod) {
      throw new FS.ErrnoError(63);
    }
    return parent.node_ops.mknod(parent, name, mode, dev);
  },
  create(path, mode) {
    mode = mode !== undefined ? mode : 438;
    mode &= 4095;
    mode |= 32768;
    return FS.mknod(path, mode, 0);
  },
  mkdir(path, mode) {
    mode = mode !== undefined ? mode : 511;
    mode &= 511 | 512;
    mode |= 16384;
    return FS.mknod(path, mode, 0);
  },
  mkdirTree(path, mode) {
    var dirs = path.split("/");
    var d = "";
    for (var i = 0; i < dirs.length; ++i) {
      if (!dirs[i]) continue;
      d += "/" + dirs[i];
      try {
        FS.mkdir(d, mode);
      } catch (e) {
        if (e.errno != 20) throw e;
      }
    }
  },
  mkdev(path, mode, dev) {
    if (typeof dev == "undefined") {
      dev = mode;
      mode = 438;
    }
    mode |= 8192;
    return FS.mknod(path, mode, dev);
  },
  symlink(oldpath, newpath) {
    if (!PATH_FS.resolve(oldpath)) {
      throw new FS.ErrnoError(44);
    }
    var lookup = FS.lookupPath(newpath, { parent: true });
    var parent = lookup.node;
    if (!parent) {
      throw new FS.ErrnoError(44);
    }
    var newname = PATH.basename(newpath);
    var errCode = FS.mayCreate(parent, newname);
    if (errCode) {
      throw new FS.ErrnoError(errCode);
    }
    if (!parent.node_ops.symlink) {
      throw new FS.ErrnoError(63);
    }
    return parent.node_ops.symlink(parent, newname, oldpath);
  },
  rename(old_path, new_path) {
    var old_dirname = PATH.dirname(old_path);
    var new_dirname = PATH.dirname(new_path);
    var old_name = PATH.basename(old_path);
    var new_name = PATH.basename(new_path);
    var lookup, old_dir, new_dir;
    lookup = FS.lookupPath(old_path, { parent: true });
    old_dir = lookup.node;
    lookup = FS.lookupPath(new_path, { parent: true });
    new_dir = lookup.node;
    if (!old_dir || !new_dir) throw new FS.ErrnoError(44);
    if (old_dir.mount !== new_dir.mount) {
      throw new FS.ErrnoError(75);
    }
    var old_node = FS.lookupNode(old_dir, old_name);
    var relative = PATH_FS.relative(old_path, new_dirname);
    if (relative.charAt(0) !== ".") {
      throw new FS.ErrnoError(28);
    }
    relative = PATH_FS.relative(new_path, old_dirname);
    if (relative.charAt(0) !== ".") {
      throw new FS.ErrnoError(55);
    }
    var new_node;
    try {
      new_node = FS.lookupNode(new_dir, new_name);
    } catch (e) {}
    if (old_node === new_node) {
      return;
    }
    var isdir = FS.isDir(old_node.mode);
    var errCode = FS.mayDelete(old_dir, old_name, isdir);
    if (errCode) {
      throw new FS.ErrnoError(errCode);
    }
    errCode = new_node
      ? FS.mayDelete(new_dir, new_name, isdir)
      : FS.mayCreate(new_dir, new_name);
    if (errCode) {
      throw new FS.ErrnoError(errCode);
    }
    if (!old_dir.node_ops.rename) {
      throw new FS.ErrnoError(63);
    }
    if (FS.isMountpoint(old_node) || (new_node && FS.isMountpoint(new_node))) {
      throw new FS.ErrnoError(10);
    }
    if (new_dir !== old_dir) {
      errCode = FS.nodePermissions(old_dir, "w");
      if (errCode) {
        throw new FS.ErrnoError(errCode);
      }
    }
    FS.hashRemoveNode(old_node);
    try {
      old_dir.node_ops.rename(old_node, new_dir, new_name);
    } catch (e) {
      throw e;
    } finally {
      FS.hashAddNode(old_node);
    }
  },
  rmdir(path) {
    var lookup = FS.lookupPath(path, { parent: true });
    var parent = lookup.node;
    var name = PATH.basename(path);
    var node = FS.lookupNode(parent, name);
    var errCode = FS.mayDelete(parent, name, true);
    if (errCode) {
      throw new FS.ErrnoError(errCode);
    }
    if (!parent.node_ops.rmdir) {
      throw new FS.ErrnoError(63);
    }
    if (FS.isMountpoint(node)) {
      throw new FS.ErrnoError(10);
    }
    parent.node_ops.rmdir(parent, name);
    FS.destroyNode(node);
  },
  readdir(path) {
    var lookup = FS.lookupPath(path, { follow: true });
    var node = lookup.node;
    if (!node.node_ops.readdir) {
      throw new FS.ErrnoError(54);
    }
    return node.node_ops.readdir(node);
  },
  unlink(path) {
    var lookup = FS.lookupPath(path, { parent: true });
    var parent = lookup.node;
    if (!parent) {
      throw new FS.ErrnoError(44);
    }
    var name = PATH.basename(path);
    var node = FS.lookupNode(parent, name);
    var errCode = FS.mayDelete(parent, name, false);
    if (errCode) {
      throw new FS.ErrnoError(errCode);
    }
    if (!parent.node_ops.unlink) {
      throw new FS.ErrnoError(63);
    }
    if (FS.isMountpoint(node)) {
      throw new FS.ErrnoError(10);
    }
    parent.node_ops.unlink(parent, name);
    FS.destroyNode(node);
  },
  readlink(path) {
    var lookup = FS.lookupPath(path);
    var link = lookup.node;
    if (!link) {
      throw new FS.ErrnoError(44);
    }
    if (!link.node_ops.readlink) {
      throw new FS.ErrnoError(28);
    }
    return PATH_FS.resolve(
      FS.getPath(link.parent),
      link.node_ops.readlink(link)
    );
  },
  stat(path, dontFollow) {
    var lookup = FS.lookupPath(path, { follow: !dontFollow });
    var node = lookup.node;
    if (!node) {
      throw new FS.ErrnoError(44);
    }
    if (!node.node_ops.getattr) {
      throw new FS.ErrnoError(63);
    }
    return node.node_ops.getattr(node);
  },
  lstat(path) {
    return FS.stat(path, true);
  },
  chmod(path, mode, dontFollow) {
    var node;
    if (typeof path == "string") {
      var lookup = FS.lookupPath(path, { follow: !dontFollow });
      node = lookup.node;
    } else {
      node = path;
    }
    if (!node.node_ops.setattr) {
      throw new FS.ErrnoError(63);
    }
    node.node_ops.setattr(node, {
      mode: (mode & 4095) | (node.mode & ~4095),
      timestamp: Date.now(),
    });
  },
  lchmod(path, mode) {
    FS.chmod(path, mode, true);
  },
  fchmod(fd, mode) {
    var stream = FS.getStreamChecked(fd);
    FS.chmod(stream.node, mode);
  },
  chown(path, uid, gid, dontFollow) {
    var node;
    if (typeof path == "string") {
      var lookup = FS.lookupPath(path, { follow: !dontFollow });
      node = lookup.node;
    } else {
      node = path;
    }
    if (!node.node_ops.setattr) {
      throw new FS.ErrnoError(63);
    }
    node.node_ops.setattr(node, { timestamp: Date.now() });
  },
  lchown(path, uid, gid) {
    FS.chown(path, uid, gid, true);
  },
  fchown(fd, uid, gid) {
    var stream = FS.getStreamChecked(fd);
    FS.chown(stream.node, uid, gid);
  },
  truncate(path, len) {
    if (len < 0) {
      throw new FS.ErrnoError(28);
    }
    var node;
    if (typeof path == "string") {
      var lookup = FS.lookupPath(path, { follow: true });
      node = lookup.node;
    } else {
      node = path;
    }
    if (!node.node_ops.setattr) {
      throw new FS.ErrnoError(63);
    }
    if (FS.isDir(node.mode)) {
      throw new FS.ErrnoError(31);
    }
    if (!FS.isFile(node.mode)) {
      throw new FS.ErrnoError(28);
    }
    var errCode = FS.nodePermissions(node, "w");
    if (errCode) {
      throw new FS.ErrnoError(errCode);
    }
    node.node_ops.setattr(node, { size: len, timestamp: Date.now() });
  },
  ftruncate(fd, len) {
    var stream = FS.getStreamChecked(fd);
    if ((stream.flags & 2097155) === 0) {
      throw new FS.ErrnoError(28);
    }
    FS.truncate(stream.node, len);
  },
  utime(path, atime, mtime) {
    var lookup = FS.lookupPath(path, { follow: true });
    var node = lookup.node;
    node.node_ops.setattr(node, { timestamp: Math.max(atime, mtime) });
  },
  open(path, flags, mode) {
    if (path === "") {
      throw new FS.ErrnoError(44);
    }
    flags = typeof flags == "string" ? FS_modeStringToFlags(flags) : flags;
    mode = typeof mode == "undefined" ? 438 : mode;
    if (flags & 64) {
      mode = (mode & 4095) | 32768;
    } else {
      mode = 0;
    }
    var node;
    if (typeof path == "object") {
      node = path;
    } else {
      path = PATH.normalize(path);
      try {
        var lookup = FS.lookupPath(path, { follow: !(flags & 131072) });
        node = lookup.node;
      } catch (e) {}
    }
    var created = false;
    if (flags & 64) {
      if (node) {
        if (flags & 128) {
          throw new FS.ErrnoError(20);
        }
      } else {
        node = FS.mknod(path, mode, 0);
        created = true;
      }
    }
    if (!node) {
      throw new FS.ErrnoError(44);
    }
    if (FS.isChrdev(node.mode)) {
      flags &= ~512;
    }
    if (flags & 65536 && !FS.isDir(node.mode)) {
      throw new FS.ErrnoError(54);
    }
    if (!created) {
      var errCode = FS.mayOpen(node, flags);
      if (errCode) {
        throw new FS.ErrnoError(errCode);
      }
    }
    if (flags & 512 && !created) {
      FS.truncate(node, 0);
    }
    flags &= ~(128 | 512 | 131072);
    var stream = FS.createStream({
      node: node,
      path: FS.getPath(node),
      flags: flags,
      seekable: true,
      position: 0,
      stream_ops: node.stream_ops,
      ungotten: [],
      error: false,
    });
    if (stream.stream_ops.open) {
      stream.stream_ops.open(stream);
    }
    if (Module["logReadFiles"] && !(flags & 1)) {
      if (!FS.readFiles) FS.readFiles = {};
      if (!(path in FS.readFiles)) {
        FS.readFiles[path] = 1;
      }
    }
    return stream;
  },
  close(stream) {
    if (FS.isClosed(stream)) {
      throw new FS.ErrnoError(8);
    }
    if (stream.getdents) stream.getdents = null;
    try {
      if (stream.stream_ops.close) {
        stream.stream_ops.close(stream);
      }
    } catch (e) {
      throw e;
    } finally {
      FS.closeStream(stream.fd);
    }
    stream.fd = null;
  },
  isClosed(stream) {
    return stream.fd === null;
  },
  llseek(stream, offset, whence) {
    if (FS.isClosed(stream)) {
      throw new FS.ErrnoError(8);
    }
    if (!stream.seekable || !stream.stream_ops.llseek) {
      throw new FS.ErrnoError(70);
    }
    if (whence != 0 && whence != 1 && whence != 2) {
      throw new FS.ErrnoError(28);
    }
    stream.position = stream.stream_ops.llseek(stream, offset, whence);
    stream.ungotten = [];
    return stream.position;
  },
  read(stream, buffer, offset, length, position) {
    if (length < 0 || position < 0) {
      throw new FS.ErrnoError(28);
    }
    if (FS.isClosed(stream)) {
      throw new FS.ErrnoError(8);
    }
    if ((stream.flags & 2097155) === 1) {
      throw new FS.ErrnoError(8);
    }
    if (FS.isDir(stream.node.mode)) {
      throw new FS.ErrnoError(31);
    }
    if (!stream.stream_ops.read) {
      throw new FS.ErrnoError(28);
    }
    var seeking = typeof position != "undefined";
    if (!seeking) {
      position = stream.position;
    } else if (!stream.seekable) {
      throw new FS.ErrnoError(70);
    }
    var bytesRead = stream.stream_ops.read(
      stream,
      buffer,
      offset,
      length,
      position
    );
    if (!seeking) stream.position += bytesRead;
    return bytesRead;
  },
  write(stream, buffer, offset, length, position, canOwn) {
    if (length < 0 || position < 0) {
      throw new FS.ErrnoError(28);
    }
    if (FS.isClosed(stream)) {
      throw new FS.ErrnoError(8);
    }
    if ((stream.flags & 2097155) === 0) {
      throw new FS.ErrnoError(8);
    }
    if (FS.isDir(stream.node.mode)) {
      throw new FS.ErrnoError(31);
    }
    if (!stream.stream_ops.write) {
      throw new FS.ErrnoError(28);
    }
    if (stream.seekable && stream.flags & 1024) {
      FS.llseek(stream, 0, 2);
    }
    var seeking = typeof position != "undefined";
    if (!seeking) {
      position = stream.position;
    } else if (!stream.seekable) {
      throw new FS.ErrnoError(70);
    }
    var bytesWritten = stream.stream_ops.write(
      stream,
      buffer,
      offset,
      length,
      position,
      canOwn
    );
    if (!seeking) stream.position += bytesWritten;
    return bytesWritten;
  },
  allocate(stream, offset, length) {
    if (FS.isClosed(stream)) {
      throw new FS.ErrnoError(8);
    }
    if (offset < 0 || length <= 0) {
      throw new FS.ErrnoError(28);
    }
    if ((stream.flags & 2097155) === 0) {
      throw new FS.ErrnoError(8);
    }
    if (!FS.isFile(stream.node.mode) && !FS.isDir(stream.node.mode)) {
      throw new FS.ErrnoError(43);
    }
    if (!stream.stream_ops.allocate) {
      throw new FS.ErrnoError(138);
    }
    stream.stream_ops.allocate(stream, offset, length);
  },
  mmap(stream, length, position, prot, flags) {
    if (
      (prot & 2) !== 0 &&
      (flags & 2) === 0 &&
      (stream.flags & 2097155) !== 2
    ) {
      throw new FS.ErrnoError(2);
    }
    if ((stream.flags & 2097155) === 1) {
      throw new FS.ErrnoError(2);
    }
    if (!stream.stream_ops.mmap) {
      throw new FS.ErrnoError(43);
    }
    return stream.stream_ops.mmap(stream, length, position, prot, flags);
  },
  msync(stream, buffer, offset, length, mmapFlags) {
    if (!stream.stream_ops.msync) {
      return 0;
    }
    return stream.stream_ops.msync(stream, buffer, offset, length, mmapFlags);
  },
  munmap: (stream) => 0,
  ioctl(stream, cmd, arg) {
    if (!stream.stream_ops.ioctl) {
      throw new FS.ErrnoError(59);
    }
    return stream.stream_ops.ioctl(stream, cmd, arg);
  },
  readFile(path, opts = {}) {
    opts.flags = opts.flags || 0;
    opts.encoding = opts.encoding || "binary";
    if (opts.encoding !== "utf8" && opts.encoding !== "binary") {
      throw new Error(`Invalid encoding type "${opts.encoding}"`);
    }
    var ret;
    var stream = FS.open(path, opts.flags);
    var stat = FS.stat(path);
    var length = stat.size;
    var buf = new Uint8Array(length);
    FS.read(stream, buf, 0, length, 0);
    if (opts.encoding === "utf8") {
      ret = UTF8ArrayToString(buf, 0);
    } else if (opts.encoding === "binary") {
      ret = buf;
    }
    FS.close(stream);
    return ret;
  },
  writeFile(path, data, opts = {}) {
    opts.flags = opts.flags || 577;
    var stream = FS.open(path, opts.flags, opts.mode);
    if (typeof data == "string") {
      var buf = new Uint8Array(lengthBytesUTF8(data) + 1);
      var actualNumBytes = stringToUTF8Array(data, buf, 0, buf.length);
      FS.write(stream, buf, 0, actualNumBytes, undefined, opts.canOwn);
    } else if (ArrayBuffer.isView(data)) {
      FS.write(stream, data, 0, data.byteLength, undefined, opts.canOwn);
    } else {
      throw new Error("Unsupported data type");
    }
    FS.close(stream);
  },
  cwd: () => FS.currentPath,
  chdir(path) {
    var lookup = FS.lookupPath(path, { follow: true });
    if (lookup.node === null) {
      throw new FS.ErrnoError(44);
    }
    if (!FS.isDir(lookup.node.mode)) {
      throw new FS.ErrnoError(54);
    }
    var errCode = FS.nodePermissions(lookup.node, "x");
    if (errCode) {
      throw new FS.ErrnoError(errCode);
    }
    FS.currentPath = lookup.path;
  },
  createDefaultDirectories() {
    FS.mkdir("/tmp");
    FS.mkdir("/home");
    FS.mkdir("/home/web_user");
  },
  createDefaultDevices() {
    FS.mkdir("/dev");
    FS.registerDevice(FS.makedev(1, 3), {
      read: () => 0,
      write: (stream, buffer, offset, length, pos) => length,
    });
    FS.mkdev("/dev/null", FS.makedev(1, 3));
    TTY.register(FS.makedev(5, 0), TTY.default_tty_ops);
    TTY.register(FS.makedev(6, 0), TTY.default_tty1_ops);
    FS.mkdev("/dev/tty", FS.makedev(5, 0));
    FS.mkdev("/dev/tty1", FS.makedev(6, 0));
    var randomBuffer = new Uint8Array(1024),
      randomLeft = 0;
    var randomByte = () => {
      if (randomLeft === 0) {
        randomLeft = randomFill(randomBuffer).byteLength;
      }
      return randomBuffer[--randomLeft];
    };
    FS.createDevice("/dev", "random", randomByte);
    FS.createDevice("/dev", "urandom", randomByte);
    FS.mkdir("/dev/shm");
    FS.mkdir("/dev/shm/tmp");
  },
  createSpecialDirectories() {
    FS.mkdir("/proc");
    var proc_self = FS.mkdir("/proc/self");
    FS.mkdir("/proc/self/fd");
    FS.mount(
      {
        mount() {
          var node = FS.createNode(proc_self, "fd", 16384 | 511, 73);
          node.node_ops = {
            lookup(parent, name) {
              var fd = +name;
              var stream = FS.getStreamChecked(fd);
              var ret = {
                parent: null,
                mount: { mountpoint: "fake" },
                node_ops: { readlink: () => stream.path },
              };
              ret.parent = ret;
              return ret;
            },
          };
          return node;
        },
      },
      {},
      "/proc/self/fd"
    );
  },
  createStandardStreams() {
    if (Module["stdin"]) {
      FS.createDevice("/dev", "stdin", Module["stdin"]);
    } else {
      FS.symlink("/dev/tty", "/dev/stdin");
    }
    if (Module["stdout"]) {
      FS.createDevice("/dev", "stdout", null, Module["stdout"]);
    } else {
      FS.symlink("/dev/tty", "/dev/stdout");
    }
    if (Module["stderr"]) {
      FS.createDevice("/dev", "stderr", null, Module["stderr"]);
    } else {
      FS.symlink("/dev/tty1", "/dev/stderr");
    }
    var stdin = FS.open("/dev/stdin", 0);
    var stdout = FS.open("/dev/stdout", 1);
    var stderr = FS.open("/dev/stderr", 1);
  },
  staticInit() {
    [44].forEach((code) => {
      FS.genericErrors[code] = new FS.ErrnoError(code);
      FS.genericErrors[code].stack = "<generic error, no stack>";
    });
    FS.nameTable = new Array(4096);
    FS.mount(MEMFS, {}, "/");
    FS.createDefaultDirectories();
    FS.createDefaultDevices();
    FS.createSpecialDirectories();
    FS.filesystems = { MEMFS: MEMFS };
  },
  init(input, output, error) {
    FS.init.initialized = true;
    Module["stdin"] = input || Module["stdin"];
    Module["stdout"] = output || Module["stdout"];
    Module["stderr"] = error || Module["stderr"];
    FS.createStandardStreams();
  },
  quit() {
    FS.init.initialized = false;
    for (var i = 0; i < FS.streams.length; i++) {
      var stream = FS.streams[i];
      if (!stream) {
        continue;
      }
      FS.close(stream);
    }
  },
  findObject(path, dontResolveLastLink) {
    var ret = FS.analyzePath(path, dontResolveLastLink);
    if (!ret.exists) {
      return null;
    }
    return ret.object;
  },
  analyzePath(path, dontResolveLastLink) {
    try {
      var lookup = FS.lookupPath(path, { follow: !dontResolveLastLink });
      path = lookup.path;
    } catch (e) {}
    var ret = {
      isRoot: false,
      exists: false,
      error: 0,
      name: null,
      path: null,
      object: null,
      parentExists: false,
      parentPath: null,
      parentObject: null,
    };
    try {
      var lookup = FS.lookupPath(path, { parent: true });
      ret.parentExists = true;
      ret.parentPath = lookup.path;
      ret.parentObject = lookup.node;
      ret.name = PATH.basename(path);
      lookup = FS.lookupPath(path, { follow: !dontResolveLastLink });
      ret.exists = true;
      ret.path = lookup.path;
      ret.object = lookup.node;
      ret.name = lookup.node.name;
      ret.isRoot = lookup.path === "/";
    } catch (e) {
      ret.error = e.errno;
    }
    return ret;
  },
  createPath(parent, path, canRead, canWrite) {
    parent = typeof parent == "string" ? parent : FS.getPath(parent);
    var parts = path.split("/").reverse();
    while (parts.length) {
      var part = parts.pop();
      if (!part) continue;
      var current = PATH.join2(parent, part);
      try {
        FS.mkdir(current);
      } catch (e) {}
      parent = current;
    }
    return current;
  },
  createFile(parent, name, properties, canRead, canWrite) {
    var path = PATH.join2(
      typeof parent == "string" ? parent : FS.getPath(parent),
      name
    );
    var mode = FS_getMode(canRead, canWrite);
    return FS.create(path, mode);
  },
  createDataFile(parent, name, data, canRead, canWrite, canOwn) {
    var path = name;
    if (parent) {
      parent = typeof parent == "string" ? parent : FS.getPath(parent);
      path = name ? PATH.join2(parent, name) : parent;
    }
    var mode = FS_getMode(canRead, canWrite);
    var node = FS.create(path, mode);
    if (data) {
      if (typeof data == "string") {
        var arr = new Array(data.length);
        for (var i = 0, len = data.length; i < len; ++i)
          arr[i] = data.charCodeAt(i);
        data = arr;
      }
      FS.chmod(node, mode | 146);
      var stream = FS.open(node, 577);
      FS.write(stream, data, 0, data.length, 0, canOwn);
      FS.close(stream);
      FS.chmod(node, mode);
    }
  },
  createDevice(parent, name, input, output) {
    var path = PATH.join2(
      typeof parent == "string" ? parent : FS.getPath(parent),
      name
    );
    var mode = FS_getMode(!!input, !!output);
    if (!FS.createDevice.major) FS.createDevice.major = 64;
    var dev = FS.makedev(FS.createDevice.major++, 0);
    FS.registerDevice(dev, {
      open(stream) {
        stream.seekable = false;
      },
      close(stream) {
        if (output?.buffer?.length) {
          output(10);
        }
      },
      read(stream, buffer, offset, length, pos) {
        var bytesRead = 0;
        for (var i = 0; i < length; i++) {
          var result;
          try {
            result = input();
          } catch (e) {
            throw new FS.ErrnoError(29);
          }
          if (result === undefined && bytesRead === 0) {
            throw new FS.ErrnoError(6);
          }
          if (result === null || result === undefined) break;
          bytesRead++;
          buffer[offset + i] = result;
        }
        if (bytesRead) {
          stream.node.timestamp = Date.now();
        }
        return bytesRead;
      },
      write(stream, buffer, offset, length, pos) {
        for (var i = 0; i < length; i++) {
          try {
            output(buffer[offset + i]);
          } catch (e) {
            throw new FS.ErrnoError(29);
          }
        }
        if (length) {
          stream.node.timestamp = Date.now();
        }
        return i;
      },
    });
    return FS.mkdev(path, mode, dev);
  },
  forceLoadFile(obj) {
    if (obj.isDevice || obj.isFolder || obj.link || obj.contents) return true;
    if (typeof XMLHttpRequest != "undefined") {
      throw new Error(
        "Lazy loading should have been performed (contents set) in createLazyFile, but it was not. Lazy loading only works in web workers. Use --embed-file or --preload-file in emcc on the main thread."
      );
    } else if (read_) {
      try {
        obj.contents = intArrayFromString(read_(obj.url), true);
        obj.usedBytes = obj.contents.length;
      } catch (e) {
        throw new FS.ErrnoError(29);
      }
    } else {
      throw new Error("Cannot load without read() or XMLHttpRequest.");
    }
  },
  createLazyFile(parent, name, url, canRead, canWrite) {
    function LazyUint8Array() {
      this.lengthKnown = false;
      this.chunks = [];
    }
    LazyUint8Array.prototype.get = function LazyUint8Array_get(idx) {
      if (idx > this.length - 1 || idx < 0) {
        return undefined;
      }
      var chunkOffset = idx % this.chunkSize;
      var chunkNum = (idx / this.chunkSize) | 0;
      return this.getter(chunkNum)[chunkOffset];
    };
    LazyUint8Array.prototype.setDataGetter =
      function LazyUint8Array_setDataGetter(getter) {
        this.getter = getter;
      };
    LazyUint8Array.prototype.cacheLength =
      function LazyUint8Array_cacheLength() {
        var xhr = new XMLHttpRequest();
        xhr.open("HEAD", url, false);
        xhr.send(null);
        if (!((xhr.status >= 200 && xhr.status < 300) || xhr.status === 304))
          throw new Error("Couldn't load " + url + ". Status: " + xhr.status);
        var datalength = Number(xhr.getResponseHeader("Content-length"));
        var header;
        var hasByteServing =
          (header = xhr.getResponseHeader("Accept-Ranges")) &&
          header === "bytes";
        var usesGzip =
          (header = xhr.getResponseHeader("Content-Encoding")) &&
          header === "gzip";
        var chunkSize = 1024 * 1024;
        if (!hasByteServing) chunkSize = datalength;
        var doXHR = (from, to) => {
          if (from > to)
            throw new Error(
              "invalid range (" + from + ", " + to + ") or no bytes requested!"
            );
          if (to > datalength - 1)
            throw new Error(
              "only " + datalength + " bytes available! programmer error!"
            );
          var xhr = new XMLHttpRequest();
          xhr.open("GET", url, false);
          if (datalength !== chunkSize)
            xhr.setRequestHeader("Range", "bytes=" + from + "-" + to);
          xhr.responseType = "arraybuffer";
          if (xhr.overrideMimeType) {
            xhr.overrideMimeType("text/plain; charset=x-user-defined");
          }
          xhr.send(null);
          if (!((xhr.status >= 200 && xhr.status < 300) || xhr.status === 304))
            throw new Error("Couldn't load " + url + ". Status: " + xhr.status);
          if (xhr.response !== undefined) {
            return new Uint8Array(xhr.response || []);
          }
          return intArrayFromString(xhr.responseText || "", true);
        };
        var lazyArray = this;
        lazyArray.setDataGetter((chunkNum) => {
          var start = chunkNum * chunkSize;
          var end = (chunkNum + 1) * chunkSize - 1;
          end = Math.min(end, datalength - 1);
          if (typeof lazyArray.chunks[chunkNum] == "undefined") {
            lazyArray.chunks[chunkNum] = doXHR(start, end);
          }
          if (typeof lazyArray.chunks[chunkNum] == "undefined")
            throw new Error("doXHR failed!");
          return lazyArray.chunks[chunkNum];
        });
        if (usesGzip || !datalength) {
          chunkSize = datalength = 1;
          datalength = this.getter(0).length;
          chunkSize = datalength;
          out(
            "LazyFiles on gzip forces download of the whole file when length is accessed"
          );
        }
        this._length = datalength;
        this._chunkSize = chunkSize;
        this.lengthKnown = true;
      };
    if (typeof XMLHttpRequest != "undefined") {
      if (!ENVIRONMENT_IS_WORKER)
        throw "Cannot do synchronous binary XHRs outside webworkers in modern browsers. Use --embed-file or --preload-file in emcc";
      var lazyArray = new LazyUint8Array();
      Object.defineProperties(lazyArray, {
        length: {
          get: function () {
            if (!this.lengthKnown) {
              this.cacheLength();
            }
            return this._length;
          },
        },
        chunkSize: {
          get: function () {
            if (!this.lengthKnown) {
              this.cacheLength();
            }
            return this._chunkSize;
          },
        },
      });
      var properties = { isDevice: false, contents: lazyArray };
    } else {
      var properties = { isDevice: false, url: url };
    }
    var node = FS.createFile(parent, name, properties, canRead, canWrite);
    if (properties.contents) {
      node.contents = properties.contents;
    } else if (properties.url) {
      node.contents = null;
      node.url = properties.url;
    }
    Object.defineProperties(node, {
      usedBytes: {
        get: function () {
          return this.contents.length;
        },
      },
    });
    var stream_ops = {};
    var keys = Object.keys(node.stream_ops);
    keys.forEach((key) => {
      var fn = node.stream_ops[key];
      stream_ops[key] = function forceLoadLazyFile() {
        FS.forceLoadFile(node);
        return fn.apply(null, arguments);
      };
    });
    function writeChunks(stream, buffer, offset, length, position) {
      var contents = stream.node.contents;
      if (position >= contents.length) return 0;
      var size = Math.min(contents.length - position, length);
      if (contents.slice) {
        for (var i = 0; i < size; i++) {
          buffer[offset + i] = contents[position + i];
        }
      } else {
        for (var i = 0; i < size; i++) {
          buffer[offset + i] = contents.get(position + i);
        }
      }
      return size;
    }
    stream_ops.read = (stream, buffer, offset, length, position) => {
      FS.forceLoadFile(node);
      return writeChunks(stream, buffer, offset, length, position);
    };
    stream_ops.mmap = (stream, length, position, prot, flags) => {
      FS.forceLoadFile(node);
      var ptr = mmapAlloc(length);
      if (!ptr) {
        throw new FS.ErrnoError(48);
      }
      writeChunks(stream, HEAP8, ptr, length, position);
      return { ptr: ptr, allocated: true };
    };
    node.stream_ops = stream_ops;
    return node;
  },
};
var UTF8ToString = (ptr, maxBytesToRead) =>
  ptr ? UTF8ArrayToString(HEAPU8, ptr, maxBytesToRead) : "";
var SYSCALLS = {
  DEFAULT_POLLMASK: 5,
  calculateAt(dirfd, path, allowEmpty) {
    if (PATH.isAbs(path)) {
      return path;
    }
    var dir;
    if (dirfd === -100) {
      dir = FS.cwd();
    } else {
      var dirstream = SYSCALLS.getStreamFromFD(dirfd);
      dir = dirstream.path;
    }
    if (path.length == 0) {
      if (!allowEmpty) {
        throw new FS.ErrnoError(44);
      }
      return dir;
    }
    return PATH.join2(dir, path);
  },
  doStat(func, path, buf) {
    var stat = func(path);
    HEAP32[buf >> 2] = stat.dev;
    HEAP32[(buf + 4) >> 2] = stat.mode;
    HEAPU32[(buf + 8) >> 2] = stat.nlink;
    HEAP32[(buf + 12) >> 2] = stat.uid;
    HEAP32[(buf + 16) >> 2] = stat.gid;
    HEAP32[(buf + 20) >> 2] = stat.rdev;
    (tempI64 = [
      stat.size >>> 0,
      ((tempDouble = stat.size),
      +Math.abs(tempDouble) >= 1
        ? tempDouble > 0
          ? +Math.floor(tempDouble / 4294967296) >>> 0
          : ~~+Math.ceil((tempDouble - +(~~tempDouble >>> 0)) / 4294967296) >>>
            0
        : 0),
    ]),
      (HEAP32[(buf + 24) >> 2] = tempI64[0]),
      (HEAP32[(buf + 28) >> 2] = tempI64[1]);
    HEAP32[(buf + 32) >> 2] = 4096;
    HEAP32[(buf + 36) >> 2] = stat.blocks;
    var atime = stat.atime.getTime();
    var mtime = stat.mtime.getTime();
    var ctime = stat.ctime.getTime();
    (tempI64 = [
      Math.floor(atime / 1e3) >>> 0,
      ((tempDouble = Math.floor(atime / 1e3)),
      +Math.abs(tempDouble) >= 1
        ? tempDouble > 0
          ? +Math.floor(tempDouble / 4294967296) >>> 0
          : ~~+Math.ceil((tempDouble - +(~~tempDouble >>> 0)) / 4294967296) >>>
            0
        : 0),
    ]),
      (HEAP32[(buf + 40) >> 2] = tempI64[0]),
      (HEAP32[(buf + 44) >> 2] = tempI64[1]);
    HEAPU32[(buf + 48) >> 2] = (atime % 1e3) * 1e3;
    (tempI64 = [
      Math.floor(mtime / 1e3) >>> 0,
      ((tempDouble = Math.floor(mtime / 1e3)),
      +Math.abs(tempDouble) >= 1
        ? tempDouble > 0
          ? +Math.floor(tempDouble / 4294967296) >>> 0
          : ~~+Math.ceil((tempDouble - +(~~tempDouble >>> 0)) / 4294967296) >>>
            0
        : 0),
    ]),
      (HEAP32[(buf + 56) >> 2] = tempI64[0]),
      (HEAP32[(buf + 60) >> 2] = tempI64[1]);
    HEAPU32[(buf + 64) >> 2] = (mtime % 1e3) * 1e3;
    (tempI64 = [
      Math.floor(ctime / 1e3) >>> 0,
      ((tempDouble = Math.floor(ctime / 1e3)),
      +Math.abs(tempDouble) >= 1
        ? tempDouble > 0
          ? +Math.floor(tempDouble / 4294967296) >>> 0
          : ~~+Math.ceil((tempDouble - +(~~tempDouble >>> 0)) / 4294967296) >>>
            0
        : 0),
    ]),
      (HEAP32[(buf + 72) >> 2] = tempI64[0]),
      (HEAP32[(buf + 76) >> 2] = tempI64[1]);
    HEAPU32[(buf + 80) >> 2] = (ctime % 1e3) * 1e3;
    (tempI64 = [
      stat.ino >>> 0,
      ((tempDouble = stat.ino),
      +Math.abs(tempDouble) >= 1
        ? tempDouble > 0
          ? +Math.floor(tempDouble / 4294967296) >>> 0
          : ~~+Math.ceil((tempDouble - +(~~tempDouble >>> 0)) / 4294967296) >>>
            0
        : 0),
    ]),
      (HEAP32[(buf + 88) >> 2] = tempI64[0]),
      (HEAP32[(buf + 92) >> 2] = tempI64[1]);
    return 0;
  },
  doMsync(addr, stream, len, flags, offset) {
    if (!FS.isFile(stream.node.mode)) {
      throw new FS.ErrnoError(43);
    }
    if (flags & 2) {
      return 0;
    }
    var buffer = HEAPU8.slice(addr, addr + len);
    FS.msync(stream, buffer, offset, len, flags);
  },
  varargs: undefined,
  get() {
    var ret = HEAP32[+SYSCALLS.varargs >> 2];
    SYSCALLS.varargs += 4;
    return ret;
  },
  getp() {
    return SYSCALLS.get();
  },
  getStr(ptr) {
    var ret = UTF8ToString(ptr);
    return ret;
  },
  getStreamFromFD(fd) {
    var stream = FS.getStreamChecked(fd);
    return stream;
  },
};
function ___syscall_fcntl64(fd, cmd, varargs) {
  SYSCALLS.varargs = varargs;
  try {
    var stream = SYSCALLS.getStreamFromFD(fd);
    switch (cmd) {
      case 0: {
        var arg = SYSCALLS.get();
        if (arg < 0) {
          return -28;
        }
        while (FS.streams[arg]) {
          arg++;
        }
        var newStream;
        newStream = FS.createStream(stream, arg);
        return newStream.fd;
      }
      case 1:
      case 2:
        return 0;
      case 3:
        return stream.flags;
      case 4: {
        var arg = SYSCALLS.get();
        stream.flags |= arg;
        return 0;
      }
      case 12: {
        var arg = SYSCALLS.getp();
        var offset = 0;
        HEAP16[(arg + offset) >> 1] = 2;
        return 0;
      }
      case 13:
      case 14:
        return 0;
    }
    return -28;
  } catch (e) {
    if (typeof FS == "undefined" || !(e.name === "ErrnoError")) throw e;
    return -e.errno;
  }
}
function ___syscall_fstat64(fd, buf) {
  try {
    var stream = SYSCALLS.getStreamFromFD(fd);
    return SYSCALLS.doStat(FS.stat, stream.path, buf);
  } catch (e) {
    if (typeof FS == "undefined" || !(e.name === "ErrnoError")) throw e;
    return -e.errno;
  }
}
var stringToUTF8 = (str, outPtr, maxBytesToWrite) =>
  stringToUTF8Array(str, HEAPU8, outPtr, maxBytesToWrite);
function ___syscall_getcwd(buf, size) {
  try {
    if (size === 0) return -28;
    var cwd = FS.cwd();
    var cwdLengthInBytes = lengthBytesUTF8(cwd) + 1;
    if (size < cwdLengthInBytes) return -68;
    stringToUTF8(cwd, buf, size);
    return cwdLengthInBytes;
  } catch (e) {
    if (typeof FS == "undefined" || !(e.name === "ErrnoError")) throw e;
    return -e.errno;
  }
}
function ___syscall_getdents64(fd, dirp, count) {
  try {
    var stream = SYSCALLS.getStreamFromFD(fd);
    stream.getdents ||= FS.readdir(stream.path);
    var struct_size = 280;
    var pos = 0;
    var off = FS.llseek(stream, 0, 1);
    var idx = Math.floor(off / struct_size);
    while (idx < stream.getdents.length && pos + struct_size <= count) {
      var id;
      var type;
      var name = stream.getdents[idx];
      if (name === ".") {
        id = stream.node.id;
        type = 4;
      } else if (name === "..") {
        var lookup = FS.lookupPath(stream.path, { parent: true });
        id = lookup.node.id;
        type = 4;
      } else {
        var child = FS.lookupNode(stream.node, name);
        id = child.id;
        type = FS.isChrdev(child.mode)
          ? 2
          : FS.isDir(child.mode)
          ? 4
          : FS.isLink(child.mode)
          ? 10
          : 8;
      }
      (tempI64 = [
        id >>> 0,
        ((tempDouble = id),
        +Math.abs(tempDouble) >= 1
          ? tempDouble > 0
            ? +Math.floor(tempDouble / 4294967296) >>> 0
            : ~~+Math.ceil(
                (tempDouble - +(~~tempDouble >>> 0)) / 4294967296
              ) >>> 0
          : 0),
      ]),
        (HEAP32[(dirp + pos) >> 2] = tempI64[0]),
        (HEAP32[(dirp + pos + 4) >> 2] = tempI64[1]);
      (tempI64 = [
        ((idx + 1) * struct_size) >>> 0,
        ((tempDouble = (idx + 1) * struct_size),
        +Math.abs(tempDouble) >= 1
          ? tempDouble > 0
            ? +Math.floor(tempDouble / 4294967296) >>> 0
            : ~~+Math.ceil(
                (tempDouble - +(~~tempDouble >>> 0)) / 4294967296
              ) >>> 0
          : 0),
      ]),
        (HEAP32[(dirp + pos + 8) >> 2] = tempI64[0]),
        (HEAP32[(dirp + pos + 12) >> 2] = tempI64[1]);
      HEAP16[(dirp + pos + 16) >> 1] = 280;
      HEAP8[(dirp + pos + 18) >> 0] = type;
      stringToUTF8(name, dirp + pos + 19, 256);
      pos += struct_size;
      idx += 1;
    }
    FS.llseek(stream, idx * struct_size, 0);
    return pos;
  } catch (e) {
    if (typeof FS == "undefined" || !(e.name === "ErrnoError")) throw e;
    return -e.errno;
  }
}
function ___syscall_ioctl(fd, op, varargs) {
  SYSCALLS.varargs = varargs;
  try {
    var stream = SYSCALLS.getStreamFromFD(fd);
    switch (op) {
      case 21509: {
        if (!stream.tty) return -59;
        return 0;
      }
      case 21505: {
        if (!stream.tty) return -59;
        if (stream.tty.ops.ioctl_tcgets) {
          var termios = stream.tty.ops.ioctl_tcgets(stream);
          var argp = SYSCALLS.getp();
          HEAP32[argp >> 2] = termios.c_iflag || 0;
          HEAP32[(argp + 4) >> 2] = termios.c_oflag || 0;
          HEAP32[(argp + 8) >> 2] = termios.c_cflag || 0;
          HEAP32[(argp + 12) >> 2] = termios.c_lflag || 0;
          for (var i = 0; i < 32; i++) {
            HEAP8[(argp + i + 17) >> 0] = termios.c_cc[i] || 0;
          }
          return 0;
        }
        return 0;
      }
      case 21510:
      case 21511:
      case 21512: {
        if (!stream.tty) return -59;
        return 0;
      }
      case 21506:
      case 21507:
      case 21508: {
        if (!stream.tty) return -59;
        if (stream.tty.ops.ioctl_tcsets) {
          var argp = SYSCALLS.getp();
          var c_iflag = HEAP32[argp >> 2];
          var c_oflag = HEAP32[(argp + 4) >> 2];
          var c_cflag = HEAP32[(argp + 8) >> 2];
          var c_lflag = HEAP32[(argp + 12) >> 2];
          var c_cc = [];
          for (var i = 0; i < 32; i++) {
            c_cc.push(HEAP8[(argp + i + 17) >> 0]);
          }
          return stream.tty.ops.ioctl_tcsets(stream.tty, op, {
            c_iflag: c_iflag,
            c_oflag: c_oflag,
            c_cflag: c_cflag,
            c_lflag: c_lflag,
            c_cc: c_cc,
          });
        }
        return 0;
      }
      case 21519: {
        if (!stream.tty) return -59;
        var argp = SYSCALLS.getp();
        HEAP32[argp >> 2] = 0;
        return 0;
      }
      case 21520: {
        if (!stream.tty) return -59;
        return -28;
      }
      case 21531: {
        var argp = SYSCALLS.getp();
        return FS.ioctl(stream, op, argp);
      }
      case 21523: {
        if (!stream.tty) return -59;
        if (stream.tty.ops.ioctl_tiocgwinsz) {
          var winsize = stream.tty.ops.ioctl_tiocgwinsz(stream.tty);
          var argp = SYSCALLS.getp();
          HEAP16[argp >> 1] = winsize[0];
          HEAP16[(argp + 2) >> 1] = winsize[1];
        }
        return 0;
      }
      case 21524: {
        if (!stream.tty) return -59;
        return 0;
      }
      case 21515: {
        if (!stream.tty) return -59;
        return 0;
      }
      default:
        return -28;
    }
  } catch (e) {
    if (typeof FS == "undefined" || !(e.name === "ErrnoError")) throw e;
    return -e.errno;
  }
}
function ___syscall_lstat64(path, buf) {
  try {
    path = SYSCALLS.getStr(path);
    return SYSCALLS.doStat(FS.lstat, path, buf);
  } catch (e) {
    if (typeof FS == "undefined" || !(e.name === "ErrnoError")) throw e;
    return -e.errno;
  }
}
function ___syscall_mkdirat(dirfd, path, mode) {
  try {
    path = SYSCALLS.getStr(path);
    path = SYSCALLS.calculateAt(dirfd, path);
    path = PATH.normalize(path);
    if (path[path.length - 1] === "/") path = path.substr(0, path.length - 1);
    FS.mkdir(path, mode, 0);
    return 0;
  } catch (e) {
    if (typeof FS == "undefined" || !(e.name === "ErrnoError")) throw e;
    return -e.errno;
  }
}
function ___syscall_newfstatat(dirfd, path, buf, flags) {
  try {
    path = SYSCALLS.getStr(path);
    var nofollow = flags & 256;
    var allowEmpty = flags & 4096;
    flags = flags & ~6400;
    path = SYSCALLS.calculateAt(dirfd, path, allowEmpty);
    return SYSCALLS.doStat(nofollow ? FS.lstat : FS.stat, path, buf);
  } catch (e) {
    if (typeof FS == "undefined" || !(e.name === "ErrnoError")) throw e;
    return -e.errno;
  }
}
function ___syscall_openat(dirfd, path, flags, varargs) {
  SYSCALLS.varargs = varargs;
  try {
    path = SYSCALLS.getStr(path);
    path = SYSCALLS.calculateAt(dirfd, path);
    var mode = varargs ? SYSCALLS.get() : 0;
    return FS.open(path, flags, mode).fd;
  } catch (e) {
    if (typeof FS == "undefined" || !(e.name === "ErrnoError")) throw e;
    return -e.errno;
  }
}
function ___syscall_readlinkat(dirfd, path, buf, bufsize) {
  try {
    path = SYSCALLS.getStr(path);
    path = SYSCALLS.calculateAt(dirfd, path);
    if (bufsize <= 0) return -28;
    var ret = FS.readlink(path);
    var len = Math.min(bufsize, lengthBytesUTF8(ret));
    var endChar = HEAP8[buf + len];
    stringToUTF8(ret, buf, bufsize + 1);
    HEAP8[buf + len] = endChar;
    return len;
  } catch (e) {
    if (typeof FS == "undefined" || !(e.name === "ErrnoError")) throw e;
    return -e.errno;
  }
}
function ___syscall_rmdir(path) {
  try {
    path = SYSCALLS.getStr(path);
    FS.rmdir(path);
    return 0;
  } catch (e) {
    if (typeof FS == "undefined" || !(e.name === "ErrnoError")) throw e;
    return -e.errno;
  }
}
function ___syscall_stat64(path, buf) {
  try {
    path = SYSCALLS.getStr(path);
    return SYSCALLS.doStat(FS.stat, path, buf);
  } catch (e) {
    if (typeof FS == "undefined" || !(e.name === "ErrnoError")) throw e;
    return -e.errno;
  }
}
function ___syscall_unlinkat(dirfd, path, flags) {
  try {
    path = SYSCALLS.getStr(path);
    path = SYSCALLS.calculateAt(dirfd, path);
    if (flags === 0) {
      FS.unlink(path);
    } else if (flags === 512) {
      FS.rmdir(path);
    } else {
      abort("Invalid flags passed to unlinkat");
    }
    return 0;
  } catch (e) {
    if (typeof FS == "undefined" || !(e.name === "ErrnoError")) throw e;
    return -e.errno;
  }
}
var nowIsMonotonic = 1;
var __emscripten_get_now_is_monotonic = () => nowIsMonotonic;
var convertI32PairToI53Checked = (lo, hi) =>
  (hi + 2097152) >>> 0 < 4194305 - !!lo ? (lo >>> 0) + hi * 4294967296 : NaN;
function __gmtime_js(time_low, time_high, tmPtr) {
  var time = convertI32PairToI53Checked(time_low, time_high);
  var date = new Date(time * 1e3);
  HEAP32[tmPtr >> 2] = date.getUTCSeconds();
  HEAP32[(tmPtr + 4) >> 2] = date.getUTCMinutes();
  HEAP32[(tmPtr + 8) >> 2] = date.getUTCHours();
  HEAP32[(tmPtr + 12) >> 2] = date.getUTCDate();
  HEAP32[(tmPtr + 16) >> 2] = date.getUTCMonth();
  HEAP32[(tmPtr + 20) >> 2] = date.getUTCFullYear() - 1900;
  HEAP32[(tmPtr + 24) >> 2] = date.getUTCDay();
  var start = Date.UTC(date.getUTCFullYear(), 0, 1, 0, 0, 0, 0);
  var yday = ((date.getTime() - start) / (1e3 * 60 * 60 * 24)) | 0;
  HEAP32[(tmPtr + 28) >> 2] = yday;
}
var isLeapYear = (year) =>
  year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0);
var MONTH_DAYS_LEAP_CUMULATIVE = [
  0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335,
];
var MONTH_DAYS_REGULAR_CUMULATIVE = [
  0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334,
];
var ydayFromDate = (date) => {
  var leap = isLeapYear(date.getFullYear());
  var monthDaysCumulative = leap
    ? MONTH_DAYS_LEAP_CUMULATIVE
    : MONTH_DAYS_REGULAR_CUMULATIVE;
  var yday = monthDaysCumulative[date.getMonth()] + date.getDate() - 1;
  return yday;
};
function __localtime_js(time_low, time_high, tmPtr) {
  var time = convertI32PairToI53Checked(time_low, time_high);
  var date = new Date(time * 1e3);
  HEAP32[tmPtr >> 2] = date.getSeconds();
  HEAP32[(tmPtr + 4) >> 2] = date.getMinutes();
  HEAP32[(tmPtr + 8) >> 2] = date.getHours();
  HEAP32[(tmPtr + 12) >> 2] = date.getDate();
  HEAP32[(tmPtr + 16) >> 2] = date.getMonth();
  HEAP32[(tmPtr + 20) >> 2] = date.getFullYear() - 1900;
  HEAP32[(tmPtr + 24) >> 2] = date.getDay();
  var yday = ydayFromDate(date) | 0;
  HEAP32[(tmPtr + 28) >> 2] = yday;
  HEAP32[(tmPtr + 36) >> 2] = -(date.getTimezoneOffset() * 60);
  var start = new Date(date.getFullYear(), 0, 1);
  var summerOffset = new Date(date.getFullYear(), 6, 1).getTimezoneOffset();
  var winterOffset = start.getTimezoneOffset();
  var dst =
    (summerOffset != winterOffset &&
      date.getTimezoneOffset() == Math.min(winterOffset, summerOffset)) | 0;
  HEAP32[(tmPtr + 32) >> 2] = dst;
}
var __mktime_js = function (tmPtr) {
  var ret = (() => {
    var date = new Date(
      HEAP32[(tmPtr + 20) >> 2] + 1900,
      HEAP32[(tmPtr + 16) >> 2],
      HEAP32[(tmPtr + 12) >> 2],
      HEAP32[(tmPtr + 8) >> 2],
      HEAP32[(tmPtr + 4) >> 2],
      HEAP32[tmPtr >> 2],
      0
    );
    var dst = HEAP32[(tmPtr + 32) >> 2];
    var guessedOffset = date.getTimezoneOffset();
    var start = new Date(date.getFullYear(), 0, 1);
    var summerOffset = new Date(date.getFullYear(), 6, 1).getTimezoneOffset();
    var winterOffset = start.getTimezoneOffset();
    var dstOffset = Math.min(winterOffset, summerOffset);
    if (dst < 0) {
      HEAP32[(tmPtr + 32) >> 2] = Number(
        summerOffset != winterOffset && dstOffset == guessedOffset
      );
    } else if (dst > 0 != (dstOffset == guessedOffset)) {
      var nonDstOffset = Math.max(winterOffset, summerOffset);
      var trueOffset = dst > 0 ? dstOffset : nonDstOffset;
      date.setTime(date.getTime() + (trueOffset - guessedOffset) * 6e4);
    }
    HEAP32[(tmPtr + 24) >> 2] = date.getDay();
    var yday = ydayFromDate(date) | 0;
    HEAP32[(tmPtr + 28) >> 2] = yday;
    HEAP32[tmPtr >> 2] = date.getSeconds();
    HEAP32[(tmPtr + 4) >> 2] = date.getMinutes();
    HEAP32[(tmPtr + 8) >> 2] = date.getHours();
    HEAP32[(tmPtr + 12) >> 2] = date.getDate();
    HEAP32[(tmPtr + 16) >> 2] = date.getMonth();
    HEAP32[(tmPtr + 20) >> 2] = date.getYear();
    var timeMs = date.getTime();
    if (isNaN(timeMs)) {
      return -1;
    }
    return timeMs / 1e3;
  })();
  return (
    setTempRet0(
      ((tempDouble = ret),
      +Math.abs(tempDouble) >= 1
        ? tempDouble > 0
          ? +Math.floor(tempDouble / 4294967296) >>> 0
          : ~~+Math.ceil((tempDouble - +(~~tempDouble >>> 0)) / 4294967296) >>>
            0
        : 0)
    ),
    ret >>> 0
  );
};
function __mmap_js(
  len,
  prot,
  flags,
  fd,
  offset_low,
  offset_high,
  allocated,
  addr
) {
  var offset = convertI32PairToI53Checked(offset_low, offset_high);
  try {
    if (isNaN(offset)) return 61;
    var stream = SYSCALLS.getStreamFromFD(fd);
    var res = FS.mmap(stream, len, offset, prot, flags);
    var ptr = res.ptr;
    HEAP32[allocated >> 2] = res.allocated;
    HEAPU32[addr >> 2] = ptr;
    return 0;
  } catch (e) {
    if (typeof FS == "undefined" || !(e.name === "ErrnoError")) throw e;
    return -e.errno;
  }
}
function __munmap_js(addr, len, prot, flags, fd, offset_low, offset_high) {
  var offset = convertI32PairToI53Checked(offset_low, offset_high);
  try {
    if (isNaN(offset)) return 61;
    var stream = SYSCALLS.getStreamFromFD(fd);
    if (prot & 2) {
      SYSCALLS.doMsync(addr, stream, len, flags, offset);
    }
    FS.munmap(stream);
  } catch (e) {
    if (typeof FS == "undefined" || !(e.name === "ErrnoError")) throw e;
    return -e.errno;
  }
}
var stringToNewUTF8 = (str) => {
  var size = lengthBytesUTF8(str) + 1;
  var ret = _malloc(size);
  if (ret) stringToUTF8(str, ret, size);
  return ret;
};
var __tzset_js = (timezone, daylight, tzname) => {
  var currentYear = new Date().getFullYear();
  var winter = new Date(currentYear, 0, 1);
  var summer = new Date(currentYear, 6, 1);
  var winterOffset = winter.getTimezoneOffset();
  var summerOffset = summer.getTimezoneOffset();
  var stdTimezoneOffset = Math.max(winterOffset, summerOffset);
  HEAPU32[timezone >> 2] = stdTimezoneOffset * 60;
  HEAP32[daylight >> 2] = Number(winterOffset != summerOffset);
  function extractZone(date) {
    var match = date.toTimeString().match(/\(([A-Za-z ]+)\)$/);
    return match ? match[1] : "GMT";
  }
  var winterName = extractZone(winter);
  var summerName = extractZone(summer);
  var winterNamePtr = stringToNewUTF8(winterName);
  var summerNamePtr = stringToNewUTF8(summerName);
  if (summerOffset < winterOffset) {
    HEAPU32[tzname >> 2] = winterNamePtr;
    HEAPU32[(tzname + 4) >> 2] = summerNamePtr;
  } else {
    HEAPU32[tzname >> 2] = summerNamePtr;
    HEAPU32[(tzname + 4) >> 2] = winterNamePtr;
  }
};
var _abort = () => {
  abort("");
};
var readEmAsmArgsArray = [];
var readEmAsmArgs = (sigPtr, buf) => {
  readEmAsmArgsArray.length = 0;
  var ch;
  while ((ch = HEAPU8[sigPtr++])) {
    var wide = ch != 105;
    wide &= ch != 112;
    buf += wide && buf % 8 ? 4 : 0;
    readEmAsmArgsArray.push(
      ch == 112
        ? HEAPU32[buf >> 2]
        : ch == 105
        ? HEAP32[buf >> 2]
        : HEAPF64[buf >> 3]
    );
    buf += wide ? 8 : 4;
  }
  return readEmAsmArgsArray;
};
var runEmAsmFunction = (code, sigPtr, argbuf) => {
  var args = readEmAsmArgs(sigPtr, argbuf);
  return ASM_CONSTS[code].apply(null, args);
};
var _emscripten_asm_const_int = (code, sigPtr, argbuf) =>
  runEmAsmFunction(code, sigPtr, argbuf);
var _emscripten_date_now = () => Date.now();
var getHeapMax = () => 2147483648;
var _emscripten_get_heap_max = () => getHeapMax();
var _emscripten_get_now;
_emscripten_get_now = () => performance.now();
var _emscripten_memcpy_js = (dest, src, num) =>
  HEAPU8.copyWithin(dest, src, src + num);
var growMemory = (size) => {
  var b = wasmMemory.buffer;
  var pages = (size - b.byteLength + 65535) / 65536;
  try {
    wasmMemory.grow(pages);
    updateMemoryViews();
    return 1;
  } catch (e) {}
};
var _emscripten_resize_heap = (requestedSize) => {
  var oldSize = HEAPU8.length;
  requestedSize >>>= 0;
  var maxHeapSize = getHeapMax();
  if (requestedSize > maxHeapSize) {
    return false;
  }
  var alignUp = (x, multiple) => x + ((multiple - (x % multiple)) % multiple);
  for (var cutDown = 1; cutDown <= 4; cutDown *= 2) {
    var overGrownHeapSize = oldSize * (1 + 0.2 / cutDown);
    overGrownHeapSize = Math.min(overGrownHeapSize, requestedSize + 100663296);
    var newSize = Math.min(
      maxHeapSize,
      alignUp(Math.max(requestedSize, overGrownHeapSize), 65536)
    );
    var replacement = growMemory(newSize);
    if (replacement) {
      return true;
    }
  }
  return false;
};
var ENV = {};
var getExecutableName = () => thisProgram || "./this.program";
var getEnvStrings = () => {
  if (!getEnvStrings.strings) {
    var lang =
      (
        (typeof navigator == "object" &&
          navigator.languages &&
          navigator.languages[0]) ||
        "C"
      ).replace("-", "_") + ".UTF-8";
    var env = {
      USER: "web_user",
      LOGNAME: "web_user",
      PATH: "/",
      PWD: "/",
      HOME: "/home/web_user",
      LANG: lang,
      _: getExecutableName(),
    };
    for (var x in ENV) {
      if (ENV[x] === undefined) delete env[x];
      else env[x] = ENV[x];
    }
    var strings = [];
    for (var x in env) {
      strings.push(`${x}=${env[x]}`);
    }
    getEnvStrings.strings = strings;
  }
  return getEnvStrings.strings;
};
var stringToAscii = (str, buffer) => {
  for (var i = 0; i < str.length; ++i) {
    HEAP8[buffer++ >> 0] = str.charCodeAt(i);
  }
  HEAP8[buffer >> 0] = 0;
};
var _environ_get = (__environ, environ_buf) => {
  var bufSize = 0;
  getEnvStrings().forEach((string, i) => {
    var ptr = environ_buf + bufSize;
    HEAPU32[(__environ + i * 4) >> 2] = ptr;
    stringToAscii(string, ptr);
    bufSize += string.length + 1;
  });
  return 0;
};
var _environ_sizes_get = (penviron_count, penviron_buf_size) => {
  var strings = getEnvStrings();
  HEAPU32[penviron_count >> 2] = strings.length;
  var bufSize = 0;
  strings.forEach((string) => (bufSize += string.length + 1));
  HEAPU32[penviron_buf_size >> 2] = bufSize;
  return 0;
};
var runtimeKeepaliveCounter = 0;
var keepRuntimeAlive = () => noExitRuntime || runtimeKeepaliveCounter > 0;
var _proc_exit = (code) => {
  EXITSTATUS = code;
  if (!keepRuntimeAlive()) {
    Module["onExit"]?.(code);
    ABORT = true;
  }
  quit_(code, new ExitStatus(code));
};
var exitJS = (status, implicit) => {
  EXITSTATUS = status;
  _proc_exit(status);
};
var _exit = exitJS;
function _fd_close(fd) {
  try {
    var stream = SYSCALLS.getStreamFromFD(fd);
    FS.close(stream);
    return 0;
  } catch (e) {
    if (typeof FS == "undefined" || !(e.name === "ErrnoError")) throw e;
    return e.errno;
  }
}
var doReadv = (stream, iov, iovcnt, offset) => {
  var ret = 0;
  for (var i = 0; i < iovcnt; i++) {
    var ptr = HEAPU32[iov >> 2];
    var len = HEAPU32[(iov + 4) >> 2];
    iov += 8;
    var curr = FS.read(stream, HEAP8, ptr, len, offset);
    if (curr < 0) return -1;
    ret += curr;
    if (curr < len) break;
    if (typeof offset !== "undefined") {
      offset += curr;
    }
  }
  return ret;
};
function _fd_read(fd, iov, iovcnt, pnum) {
  try {
    var stream = SYSCALLS.getStreamFromFD(fd);
    var num = doReadv(stream, iov, iovcnt);
    HEAPU32[pnum >> 2] = num;
    return 0;
  } catch (e) {
    if (typeof FS == "undefined" || !(e.name === "ErrnoError")) throw e;
    return e.errno;
  }
}
function _fd_seek(fd, offset_low, offset_high, whence, newOffset) {
  var offset = convertI32PairToI53Checked(offset_low, offset_high);
  try {
    if (isNaN(offset)) return 61;
    var stream = SYSCALLS.getStreamFromFD(fd);
    FS.llseek(stream, offset, whence);
    (tempI64 = [
      stream.position >>> 0,
      ((tempDouble = stream.position),
      +Math.abs(tempDouble) >= 1
        ? tempDouble > 0
          ? +Math.floor(tempDouble / 4294967296) >>> 0
          : ~~+Math.ceil((tempDouble - +(~~tempDouble >>> 0)) / 4294967296) >>>
            0
        : 0),
    ]),
      (HEAP32[newOffset >> 2] = tempI64[0]),
      (HEAP32[(newOffset + 4) >> 2] = tempI64[1]);
    if (stream.getdents && offset === 0 && whence === 0) stream.getdents = null;
    return 0;
  } catch (e) {
    if (typeof FS == "undefined" || !(e.name === "ErrnoError")) throw e;
    return e.errno;
  }
}
var doWritev = (stream, iov, iovcnt, offset) => {
  var ret = 0;
  for (var i = 0; i < iovcnt; i++) {
    var ptr = HEAPU32[iov >> 2];
    var len = HEAPU32[(iov + 4) >> 2];
    iov += 8;
    var curr = FS.write(stream, HEAP8, ptr, len, offset);
    if (curr < 0) return -1;
    ret += curr;
    if (typeof offset !== "undefined") {
      offset += curr;
    }
  }
  return ret;
};
function _fd_write(fd, iov, iovcnt, pnum) {
  try {
    var stream = SYSCALLS.getStreamFromFD(fd);
    var num = doWritev(stream, iov, iovcnt);
    HEAPU32[pnum >> 2] = num;
    return 0;
  } catch (e) {
    if (typeof FS == "undefined" || !(e.name === "ErrnoError")) throw e;
    return e.errno;
  }
}
var arraySum = (array, index) => {
  var sum = 0;
  for (var i = 0; i <= index; sum += array[i++]) {}
  return sum;
};
var MONTH_DAYS_LEAP = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
var MONTH_DAYS_REGULAR = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
var addDays = (date, days) => {
  var newDate = new Date(date.getTime());
  while (days > 0) {
    var leap = isLeapYear(newDate.getFullYear());
    var currentMonth = newDate.getMonth();
    var daysInCurrentMonth = (leap ? MONTH_DAYS_LEAP : MONTH_DAYS_REGULAR)[
      currentMonth
    ];
    if (days > daysInCurrentMonth - newDate.getDate()) {
      days -= daysInCurrentMonth - newDate.getDate() + 1;
      newDate.setDate(1);
      if (currentMonth < 11) {
        newDate.setMonth(currentMonth + 1);
      } else {
        newDate.setMonth(0);
        newDate.setFullYear(newDate.getFullYear() + 1);
      }
    } else {
      newDate.setDate(newDate.getDate() + days);
      return newDate;
    }
  }
  return newDate;
};
var writeArrayToMemory = (array, buffer) => {
  HEAP8.set(array, buffer);
};
var _strftime = (s, maxsize, format, tm) => {
  var tm_zone = HEAPU32[(tm + 40) >> 2];
  var date = {
    tm_sec: HEAP32[tm >> 2],
    tm_min: HEAP32[(tm + 4) >> 2],
    tm_hour: HEAP32[(tm + 8) >> 2],
    tm_mday: HEAP32[(tm + 12) >> 2],
    tm_mon: HEAP32[(tm + 16) >> 2],
    tm_year: HEAP32[(tm + 20) >> 2],
    tm_wday: HEAP32[(tm + 24) >> 2],
    tm_yday: HEAP32[(tm + 28) >> 2],
    tm_isdst: HEAP32[(tm + 32) >> 2],
    tm_gmtoff: HEAP32[(tm + 36) >> 2],
    tm_zone: tm_zone ? UTF8ToString(tm_zone) : "",
  };
  var pattern = UTF8ToString(format);
  var EXPANSION_RULES_1 = {
    "%c": "%a %b %d %H:%M:%S %Y",
    "%D": "%m/%d/%y",
    "%F": "%Y-%m-%d",
    "%h": "%b",
    "%r": "%I:%M:%S %p",
    "%R": "%H:%M",
    "%T": "%H:%M:%S",
    "%x": "%m/%d/%y",
    "%X": "%H:%M:%S",
    "%Ec": "%c",
    "%EC": "%C",
    "%Ex": "%m/%d/%y",
    "%EX": "%H:%M:%S",
    "%Ey": "%y",
    "%EY": "%Y",
    "%Od": "%d",
    "%Oe": "%e",
    "%OH": "%H",
    "%OI": "%I",
    "%Om": "%m",
    "%OM": "%M",
    "%OS": "%S",
    "%Ou": "%u",
    "%OU": "%U",
    "%OV": "%V",
    "%Ow": "%w",
    "%OW": "%W",
    "%Oy": "%y",
  };
  for (var rule in EXPANSION_RULES_1) {
    pattern = pattern.replace(new RegExp(rule, "g"), EXPANSION_RULES_1[rule]);
  }
  var WEEKDAYS = [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
  ];
  var MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
  ];
  function leadingSomething(value, digits, character) {
    var str = typeof value == "number" ? value.toString() : value || "";
    while (str.length < digits) {
      str = character[0] + str;
    }
    return str;
  }
  function leadingNulls(value, digits) {
    return leadingSomething(value, digits, "0");
  }
  function compareByDay(date1, date2) {
    function sgn(value) {
      return value < 0 ? -1 : value > 0 ? 1 : 0;
    }
    var compare;
    if ((compare = sgn(date1.getFullYear() - date2.getFullYear())) === 0) {
      if ((compare = sgn(date1.getMonth() - date2.getMonth())) === 0) {
        compare = sgn(date1.getDate() - date2.getDate());
      }
    }
    return compare;
  }
  function getFirstWeekStartDate(janFourth) {
    switch (janFourth.getDay()) {
      case 0:
        return new Date(janFourth.getFullYear() - 1, 11, 29);
      case 1:
        return janFourth;
      case 2:
        return new Date(janFourth.getFullYear(), 0, 3);
      case 3:
        return new Date(janFourth.getFullYear(), 0, 2);
      case 4:
        return new Date(janFourth.getFullYear(), 0, 1);
      case 5:
        return new Date(janFourth.getFullYear() - 1, 11, 31);
      case 6:
        return new Date(janFourth.getFullYear() - 1, 11, 30);
    }
  }
  function getWeekBasedYear(date) {
    var thisDate = addDays(new Date(date.tm_year + 1900, 0, 1), date.tm_yday);
    var janFourthThisYear = new Date(thisDate.getFullYear(), 0, 4);
    var janFourthNextYear = new Date(thisDate.getFullYear() + 1, 0, 4);
    var firstWeekStartThisYear = getFirstWeekStartDate(janFourthThisYear);
    var firstWeekStartNextYear = getFirstWeekStartDate(janFourthNextYear);
    if (compareByDay(firstWeekStartThisYear, thisDate) <= 0) {
      if (compareByDay(firstWeekStartNextYear, thisDate) <= 0) {
        return thisDate.getFullYear() + 1;
      }
      return thisDate.getFullYear();
    }
    return thisDate.getFullYear() - 1;
  }
  var EXPANSION_RULES_2 = {
    "%a": (date) => WEEKDAYS[date.tm_wday].substring(0, 3),
    "%A": (date) => WEEKDAYS[date.tm_wday],
    "%b": (date) => MONTHS[date.tm_mon].substring(0, 3),
    "%B": (date) => MONTHS[date.tm_mon],
    "%C": (date) => {
      var year = date.tm_year + 1900;
      return leadingNulls((year / 100) | 0, 2);
    },
    "%d": (date) => leadingNulls(date.tm_mday, 2),
    "%e": (date) => leadingSomething(date.tm_mday, 2, " "),
    "%g": (date) => getWeekBasedYear(date).toString().substring(2),
    "%G": getWeekBasedYear,
    "%H": (date) => leadingNulls(date.tm_hour, 2),
    "%I": (date) => {
      var twelveHour = date.tm_hour;
      if (twelveHour == 0) twelveHour = 12;
      else if (twelveHour > 12) twelveHour -= 12;
      return leadingNulls(twelveHour, 2);
    },
    "%j": (date) =>
      leadingNulls(
        date.tm_mday +
          arraySum(
            isLeapYear(date.tm_year + 1900)
              ? MONTH_DAYS_LEAP
              : MONTH_DAYS_REGULAR,
            date.tm_mon - 1
          ),
        3
      ),
    "%m": (date) => leadingNulls(date.tm_mon + 1, 2),
    "%M": (date) => leadingNulls(date.tm_min, 2),
    "%n": () => "\n",
    "%p": (date) => {
      if (date.tm_hour >= 0 && date.tm_hour < 12) {
        return "AM";
      }
      return "PM";
    },
    "%S": (date) => leadingNulls(date.tm_sec, 2),
    "%t": () => "\t",
    "%u": (date) => date.tm_wday || 7,
    "%U": (date) => {
      var days = date.tm_yday + 7 - date.tm_wday;
      return leadingNulls(Math.floor(days / 7), 2);
    },
    "%V": (date) => {
      var val = Math.floor((date.tm_yday + 7 - ((date.tm_wday + 6) % 7)) / 7);
      if ((date.tm_wday + 371 - date.tm_yday - 2) % 7 <= 2) {
        val++;
      }
      if (!val) {
        val = 52;
        var dec31 = (date.tm_wday + 7 - date.tm_yday - 1) % 7;
        if (
          dec31 == 4 ||
          (dec31 == 5 && isLeapYear((date.tm_year % 400) - 1))
        ) {
          val++;
        }
      } else if (val == 53) {
        var jan1 = (date.tm_wday + 371 - date.tm_yday) % 7;
        if (jan1 != 4 && (jan1 != 3 || !isLeapYear(date.tm_year))) val = 1;
      }
      return leadingNulls(val, 2);
    },
    "%w": (date) => date.tm_wday,
    "%W": (date) => {
      var days = date.tm_yday + 7 - ((date.tm_wday + 6) % 7);
      return leadingNulls(Math.floor(days / 7), 2);
    },
    "%y": (date) => (date.tm_year + 1900).toString().substring(2),
    "%Y": (date) => date.tm_year + 1900,
    "%z": (date) => {
      var off = date.tm_gmtoff;
      var ahead = off >= 0;
      off = Math.abs(off) / 60;
      off = (off / 60) * 100 + (off % 60);
      return (ahead ? "+" : "-") + String("0000" + off).slice(-4);
    },
    "%Z": (date) => date.tm_zone,
    "%%": () => "%",
  };
  pattern = pattern.replace(/%%/g, "\0\0");
  for (var rule in EXPANSION_RULES_2) {
    if (pattern.includes(rule)) {
      pattern = pattern.replace(
        new RegExp(rule, "g"),
        EXPANSION_RULES_2[rule](date)
      );
    }
  }
  pattern = pattern.replace(/\0\0/g, "%");
  var bytes = intArrayFromString(pattern, false);
  if (bytes.length > maxsize) {
    return 0;
  }
  writeArrayToMemory(bytes, s);
  return bytes.length - 1;
};
var _strftime_l = (s, maxsize, format, tm, loc) =>
  _strftime(s, maxsize, format, tm);
var getCFunc = (ident) => {
  var func = Module["_" + ident];
  return func;
};
var stringToUTF8OnStack = (str) => {
  var size = lengthBytesUTF8(str) + 1;
  var ret = stackAlloc(size);
  stringToUTF8(str, ret, size);
  return ret;
};
var ccall = (ident, returnType, argTypes, args, opts) => {
  var toC = {
    string: (str) => {
      var ret = 0;
      if (str !== null && str !== undefined && str !== 0) {
        ret = stringToUTF8OnStack(str);
      }
      return ret;
    },
    array: (arr) => {
      var ret = stackAlloc(arr.length);
      writeArrayToMemory(arr, ret);
      return ret;
    },
  };
  function convertReturnValue(ret) {
    if (returnType === "string") {
      return UTF8ToString(ret);
    }
    if (returnType === "boolean") return Boolean(ret);
    return ret;
  }
  var func = getCFunc(ident);
  var cArgs = [];
  var stack = 0;
  if (args) {
    for (var i = 0; i < args.length; i++) {
      var converter = toC[argTypes[i]];
      if (converter) {
        if (stack === 0) stack = stackSave();
        cArgs[i] = converter(args[i]);
      } else {
        cArgs[i] = args[i];
      }
    }
  }
  var ret = func.apply(null, cArgs);
  function onDone(ret) {
    if (stack !== 0) stackRestore(stack);
    return convertReturnValue(ret);
  }
  ret = onDone(ret);
  return ret;
};
var FSNode = function (parent, name, mode, rdev) {
  if (!parent) {
    parent = this;
  }
  this.parent = parent;
  this.mount = parent.mount;
  this.mounted = null;
  this.id = FS.nextInode++;
  this.name = name;
  this.mode = mode;
  this.node_ops = {};
  this.stream_ops = {};
  this.rdev = rdev;
};
var readMode = 292 | 73;
var writeMode = 146;
Object.defineProperties(FSNode.prototype, {
  read: {
    get: function () {
      return (this.mode & readMode) === readMode;
    },
    set: function (val) {
      val ? (this.mode |= readMode) : (this.mode &= ~readMode);
    },
  },
  write: {
    get: function () {
      return (this.mode & writeMode) === writeMode;
    },
    set: function (val) {
      val ? (this.mode |= writeMode) : (this.mode &= ~writeMode);
    },
  },
  isFolder: {
    get: function () {
      return FS.isDir(this.mode);
    },
  },
  isDevice: {
    get: function () {
      return FS.isChrdev(this.mode);
    },
  },
});
FS.FSNode = FSNode;
FS.createPreloadedFile = FS_createPreloadedFile;
FS.staticInit();
Module["FS_createPath"] = FS.createPath;
Module["FS_createDataFile"] = FS.createDataFile;
Module["FS_createPreloadedFile"] = FS.createPreloadedFile;
Module["FS_unlink"] = FS.unlink;
Module["FS_createLazyFile"] = FS.createLazyFile;
Module["FS_createDevice"] = FS.createDevice;
var wasmImports = {
  a: ___cxa_throw,
  e: ___syscall_fcntl64,
  G: ___syscall_fstat64,
  y: ___syscall_getcwd,
  B: ___syscall_getdents64,
  I: ___syscall_ioctl,
  D: ___syscall_lstat64,
  C: ___syscall_mkdirat,
  E: ___syscall_newfstatat,
  l: ___syscall_openat,
  x: ___syscall_readlinkat,
  z: ___syscall_rmdir,
  F: ___syscall_stat64,
  A: ___syscall_unlinkat,
  J: __emscripten_get_now_is_monotonic,
  s: __gmtime_js,
  t: __localtime_js,
  u: __mktime_js,
  q: __mmap_js,
  r: __munmap_js,
  H: __tzset_js,
  f: _abort,
  w: _emscripten_asm_const_int,
  i: _emscripten_date_now,
  m: _emscripten_get_heap_max,
  c: _emscripten_get_now,
  K: _emscripten_memcpy_js,
  p: _emscripten_resize_heap,
  n: _environ_get,
  o: _environ_sizes_get,
  b: _exit,
  g: _fd_close,
  k: _fd_read,
  v: _fd_seek,
  h: _fd_write,
  j: _strftime,
  d: _strftime_l,
};
var wasmExports = createWasm();
var ___wasm_call_ctors = () => (___wasm_call_ctors = wasmExports["M"])();
var _MyPrint = (Module["_MyPrint"] = (a0) =>
  (_MyPrint = Module["_MyPrint"] = wasmExports["N"])(a0));
var _CopyHeap = (Module["_CopyHeap"] = (a0, a1, a2) =>
  (_CopyHeap = Module["_CopyHeap"] = wasmExports["O"])(a0, a1, a2));
var _SherpaOnnxCreateOfflineTts = (Module["_SherpaOnnxCreateOfflineTts"] = (
  a0
) =>
  (_SherpaOnnxCreateOfflineTts = Module["_SherpaOnnxCreateOfflineTts"] =
    wasmExports["P"])(a0));
var _SherpaOnnxDestroyOfflineTts = (Module["_SherpaOnnxDestroyOfflineTts"] = (
  a0
) =>
  (_SherpaOnnxDestroyOfflineTts = Module["_SherpaOnnxDestroyOfflineTts"] =
    wasmExports["Q"])(a0));
var _SherpaOnnxOfflineTtsSampleRate = (Module[
  "_SherpaOnnxOfflineTtsSampleRate"
] = (a0) =>
  (_SherpaOnnxOfflineTtsSampleRate = Module["_SherpaOnnxOfflineTtsSampleRate"] =
    wasmExports["R"])(a0));
var _SherpaOnnxOfflineTtsNumSpeakers = (Module[
  "_SherpaOnnxOfflineTtsNumSpeakers"
] = (a0) =>
  (_SherpaOnnxOfflineTtsNumSpeakers = Module[
    "_SherpaOnnxOfflineTtsNumSpeakers"
  ] =
    wasmExports["S"])(a0));
var _SherpaOnnxOfflineTtsGenerate = (Module["_SherpaOnnxOfflineTtsGenerate"] = (
  a0,
  a1,
  a2,
  a3
) =>
  (_SherpaOnnxOfflineTtsGenerate = Module["_SherpaOnnxOfflineTtsGenerate"] =
    wasmExports["T"])(a0, a1, a2, a3));
var _SherpaOnnxOfflineTtsGenerateWithCallback = (Module[
  "_SherpaOnnxOfflineTtsGenerateWithCallback"
] = (a0, a1, a2, a3, a4) =>
  (_SherpaOnnxOfflineTtsGenerateWithCallback = Module[
    "_SherpaOnnxOfflineTtsGenerateWithCallback"
  ] =
    wasmExports["U"])(a0, a1, a2, a3, a4));
var _SherpaOnnxDestroyOfflineTtsGeneratedAudio = (Module[
  "_SherpaOnnxDestroyOfflineTtsGeneratedAudio"
] = (a0) =>
  (_SherpaOnnxDestroyOfflineTtsGeneratedAudio = Module[
    "_SherpaOnnxDestroyOfflineTtsGeneratedAudio"
  ] =
    wasmExports["V"])(a0));
var _SherpaOnnxWriteWave = (Module["_SherpaOnnxWriteWave"] = (a0, a1, a2, a3) =>
  (_SherpaOnnxWriteWave = Module["_SherpaOnnxWriteWave"] = wasmExports["W"])(
    a0,
    a1,
    a2,
    a3
  ));
var _malloc = (Module["_malloc"] = (a0) =>
  (_malloc = Module["_malloc"] = wasmExports["Y"])(a0));
var _free = (Module["_free"] = (a0) =>
  (_free = Module["_free"] = wasmExports["Z"])(a0));
var _emscripten_builtin_memalign = (a0, a1) =>
  (_emscripten_builtin_memalign = wasmExports["_"])(a0, a1);
var setTempRet0 = (a0) => (setTempRet0 = wasmExports["$"])(a0);
var stackSave = () => (stackSave = wasmExports["aa"])();
var stackRestore = (a0) => (stackRestore = wasmExports["ba"])(a0);
var stackAlloc = (a0) => (stackAlloc = wasmExports["ca"])(a0);
var ___cxa_is_pointer_type = (a0) =>
  (___cxa_is_pointer_type = wasmExports["da"])(a0);
Module["addRunDependency"] = addRunDependency;
Module["removeRunDependency"] = removeRunDependency;
Module["FS_createPath"] = FS.createPath;
Module["FS_createLazyFile"] = FS.createLazyFile;
Module["FS_createDevice"] = FS.createDevice;
Module["ccall"] = ccall;
Module["setValue"] = setValue;
Module["getValue"] = getValue;
Module["UTF8ToString"] = UTF8ToString;
Module["stringToUTF8"] = stringToUTF8;
Module["lengthBytesUTF8"] = lengthBytesUTF8;
Module["FS_createPreloadedFile"] = FS.createPreloadedFile;
Module["FS_createDataFile"] = FS.createDataFile;
Module["FS_unlink"] = FS.unlink;
var calledRun;
dependenciesFulfilled = function runCaller() {
  if (!calledRun) run();
  if (!calledRun) dependenciesFulfilled = runCaller;
};
function run() {
  if (runDependencies > 0) {
    return;
  }
  preRun();
  if (runDependencies > 0) {
    return;
  }
  function doRun() {
    if (calledRun) return;
    calledRun = true;
    Module["calledRun"] = true;
    if (ABORT) return;
    initRuntime();
    if (Module["onRuntimeInitialized"]) Module["onRuntimeInitialized"]();
    postRun();
  }
  if (Module["setStatus"]) {
    Module["setStatus"]("Running...");
    setTimeout(function () {
      setTimeout(function () {
        Module["setStatus"]("");
      }, 1);
      doRun();
    }, 1);
  } else {
    doRun();
  }
}
if (Module["preInit"]) {
  if (typeof Module["preInit"] == "function")
    Module["preInit"] = [Module["preInit"]];
  while (Module["preInit"].length > 0) {
    Module["preInit"].pop()();
  }
}
run();
