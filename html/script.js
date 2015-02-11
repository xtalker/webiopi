
webiopi().ready(function() {

    // Globals
    var UnreadCnt = 0; Subject = "--"
    var Temp3 = 0; Humid3 = 0; Bat3 = 0; Last3 = "-";
    
    // Create a button to call setLightHours macro
    // var sendButton = webiopi().createButton("testButton", "Test", function() {
    //     document.getElementById("TestLabel").innerText="Done!";
    // });

    // var mailCntbutton = webiopi().createButton("mailCnt", "Count", callMailMacro);
    // var mailSubjbutton = webiopi().createButton("mailSubj", "Subject", callMailMacro);
    // Create led buttons
    var button3 = webiopi().createGPIOButton(17, "No Mail");
    var button4 = webiopi().createGPIOButton(9, "Mail");
    var button5 = webiopi().createGPIOButton(22, "Heartbeat");
    var button1 = webiopi().createGPIOButton(4, "Red1");
    var button2 = webiopi().createGPIOButton(10, "Checking");

    // Append the button to the controls box using a jQuery function
    //$("#controls").append(sendButton);
    // $("#controls").append(mailCntbutton);
    // $("#controls").append(mailSubjbutton);
    $("#controls").append(button1);
    $("#controls").append(button3);
    $("#controls").append(button4);
    $("#controls").append(button5);
    $("#controls").append(button2);

    function callMailMacro(){
        webiopi().callMacro("checkMail", [], macro_Mail_Callback);
    }

    function macro_Mail_Callback(macro, args, data){
        var temp = data.split(",");
        webiopi().setLabel("mailCnt", "Count: " + temp[0]);
        webiopi().setLabel("mailSubj", temp[1]);
        UnreadCnt = temp[0]; 
        Subject   = temp[1];
    }

    function callTemp3Macro(){
        webiopi().callMacro("wsTemp3", [], macro_Temp3_Callback);
    }

    function macro_Temp3_Callback(macro, args, data){
        var temp = data.split(",");
        Temp3 = temp[0];
        Humid3 = temp[1];
        Bat3 = temp[2];
        Last3 = temp[3];
        // console.log("Temp3 = %o : %o : %o : %o",Temp3,Humid3,Bat3,Last3)
    }

    setInterval (callMailMacro, 6000);
    setInterval (callTemp3Macro, 6000);

    // Refresh GPIO buttons
    // pass true to refresh repeatedly of false to refresh once
    webiopi().refreshGPIO(true);

    var t3_1 = new JustGage({
        id: "gauge_t3_1",
        value: Temp3,
        min: 0,
        max: 100,
        symbol: '°',
        customSectors: [{
          color : "#008000", // Yellow
          lo : 0,
          hi : 60
        },{
          color : "#FFFF00",  // Green
          lo : 60,
          hi : 70
        }, {
          color : "#FF0000", // Red
          lo : 70,
          hi : 100
        }],
        relativeGaugeSize: true,
        title: "Temperature"
    });

    var t3_2 = new JustGage({
        id: "gauge_t3_2",
        value: Humid3,
        min: 0,
        max: 100,
        symbol: '%',
        relativeGaugeSize: true,
        title: "Humidity"
    });

    var t3_3 = new JustGage({
        id: "gauge_t3_3",
        value: Bat3,
        min: 0,
        max: 10,
        decimals: 2,
        symbol: 'V',
        customSectors: [{
          color : "#FFFF00",  // Red
          lo : 0,
          hi : 5
        },{
          color : "#008000",  // Green
          lo : 5,
          hi : 10
        }],
        relativeGaugeSize: true,
        title: "Sensor Battery"
    });

    var e1 = new JustGage({
        id: "email_1",
        value: UnreadCnt,
        min: 0,
        max: 20,
        decimals: 0,
        symbol: '',
        relativeGaugeSize: true,
        title: "Unread Emails"
    });

    setInterval(function() {
        t3_1.refresh(Temp3);
        t3_2.refresh(Humid3);
        t3_3.refresh(Bat3);
        e1.refresh(UnreadCnt);
        document.getElementById("t3_time").innerText=Last3;
        document.getElementById("email_2_subject").innerText=Subject;
    }, 6000);

});
