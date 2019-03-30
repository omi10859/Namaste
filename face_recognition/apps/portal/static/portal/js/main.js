    /** CSRF Protection **/
    var csrf = $("[name=csrfmiddlewaretoken]").val();

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrf);
            }
        }
    });
    /** End CSRF Protection **/

    var imageSuccessCount = 0,
        imagePending = 0;
    var imageData = [];
    var avatar = $("#avatar");
    var status_text = $(".status_text");
    var canvas = document.getElementById("canvas");
    var video = document.getElementById("video");
    var alert = $("#mainAlert");
    var progress = $("#imageProgress");
    var vstream = null;
    var available_mood_classes = ["fa-smile-beam", "fa-frown-open", "fa-angry"];
    var terminal = $("#terminalttx");
    var user = null;

    function GetCameraPermissions() {
        if (!navigator.mediaDevices) {
            alert("MediaDevices API is not supported on your browser! Exiting!");
            return;
        }
        if (!navigator.mediaDevices.enumerateDevices)
            $("#cameraPopup").show();
        return navigator.mediaDevices.getUserMedia({
            video: true,
            // audio: true
        }).then(cameraInitialized);
    }

    function resetCaptureFrames() {
        imageSuccessCount = 0;
        imagePending = 0;
        imageData = [];
    }

    function cameraInitialized(stream) {
        $("#cameraPopup").fadeOut();
        video.srcObject = stream;
        vstream = stream;
        video.play();
        avatar.fadeOut();
        $("#video").fadeIn();
    }

    function startCapturingFrames(callback) {

        console.log("Starting");
        $("#faceDetector").fadeIn();
        var frame = captureFrame();
        callback(frame);
    }

    function captureFrame() {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        var context = canvas.getContext('2d');
        context.drawImage(video, 0, 0, video.videoWidth, video.videoHeight);
        var data = canvas.toDataURL();
        return data;
    }

    function stopCapturingFrames() {
        vstream.getTracks()[0].stop();
    }

    function startMoodDetection(frame) {
        logTerminal("Preparing Mood Detection Engine...");
        stopCapturingFrames();
        let payload = prepareImagePayload(frame);
        // logTerminal("Preparing Payload for server...Connecting to server...");
        $(".current_mood").html($(".current_mood").html() + ' <i class="fas fa-spin fa-circle-notch"></i>');
        $.ajax({
            url: api_endpoints['detect_mood'],
            data: payload,
            type: 'POST',
            success: function (response) {
                if (response.status) {
                    moodData = response.mood;
                    loadMoodData();
                } else {
                    $(".current_mood").html("Error!");
                }
            }
        });
    }

    function loadMusic(emotion) {}

    function getB64Data(data) {
        // return data;
        return data.split(",")[1];
    }

    function prepareImagePayload(data) {
        var b64Image = getB64Data(data);
        var postData = {
            "image": b64Image
        };
        console.log(postData)
        return postData;
    }

    function setClock() {
        let days = ["Mon", "Tues", "Wed", "Thurs", "Fri", "Sat", "Sun"];
        let months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "December"];
        setInterval(function (e) {
            var curr = new Date();
            $("#date_num").html(curr.getDate());
            $("#time_num").html(curr.getHours() + ":" + curr.getMinutes());
            $("#day").html(days[curr.getDay() - 1]);
            $("#month").html(months[curr.getMonth()]);
            $("#second").html(curr.getSeconds());
        }, 1000);
    }

    function loadUser() {
        if (user != null)
            return
        $.ajax({
            url: api_endpoints['get-logged-in-user'],
            method: 'GET',
            dataType: 'JSON',
            success: function (response) {
                if (response.status) {
                    user = response.data;
                    loadUserData();
                } else {
                    window.location.reload();
                }
            }
        })
    }

    function loadUserData() {
        if (user == null)
            return

        logTerminal("Initialising user data, Hello " + user.name);

        $(".user_name").html(user.name);
    }

    function loadMoodData() {
        if (moodData == null)
            return
        $(".current_mood").html(moodData);
        logTerminal("You seem to be " + moodData + "...");
        setTimeout(function () {
            GetCameraPermissions();
            $(video).one('canplay', function () {
                startCapturingFrames(startMoodDetection);
            });
        }, 60000);
    }

    var terminal_queue = ["Initialising", ];
    var typed = null;
    var terminal_empty = true;

    function logTerminal(msg) {
        terminal_queue.push(msg);
    }

    function loadNextForTerminal() {
        console.log("Poll");
        console.log(terminal_queue);
        console.log(terminal_empty);
        if (!terminal_empty) return;
        if (terminal_queue.length == 0) return;
        // if(typed) typed.destroy();
        terminal_empty = false;
        terminal.fadeIn();
        typed = new Typed(terminal[0], {
            strings: ["", terminal_queue.shift()],
            typeSpeed: 5,
            loop: false,
            loopCount: 1,
            contentType: 'html',
            backDelay: 200,
            onStart: function (self) {
                // terminal.fadeIn();
                terminal_empty = false;
            },
            onComplete: function (self) {
                setTimeout(function () {
                    terminal.fadeOut();
                    setTimeout(function () {
                        typed.destroy();
                        terminal_empty = true;
                    }, 500);
                }, 500);
            },
            onDestroy: function (self) {
                // terminal_empty = true;
            }
        });
    }

    function init() {
        $("#cameraInitialisePopup").show();
        setInterval(function () {
            loadNextForTerminal();
        }, 1000);

        setClock();
        loadUser();
        GetCameraPermissions();
        $("#cameraInitialisePopup").fadeOut();
        $(video).one('canplay', function () {
            // logTerminal("Starting Mood Detection...");
            startCapturingFrames(startMoodDetection);
        });
    }

    init();