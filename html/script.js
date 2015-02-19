

webiopi().ready(function() {

    // Globals
    var UnreadCnt = 0; Subject = "--"
    var Motion2 = 0; Node2TS = "-"; Bat2 = 0;
    var Temp3 = 0; Humid3 = 0; Light3 = 0; Bat3 = 0; Node3TS = "-";
    var Temp4 = 0; Humid4 = 0; Light4 = 0; Bat4 = 0; Node4TS = "-";

    // Create led buttons
    var button3 = webiopi().createGPIOButton(17, "No Mail");
    var button4 = webiopi().createGPIOButton(9, "Mail");
    var button5 = webiopi().createGPIOButton(22, "Heartbeat");
    var button1 = webiopi().createGPIOButton(4, "Red1");
    var button2 = webiopi().createGPIOButton(10, "Checking");

    // Append the button to the controls box using a jQuery function
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

    function callNode2Macro(){
        webiopi().callMacro("wsNode2", [], macro_Node2_Callback);
    }
    function macro_Node2_Callback(macro, args, data){
        var temp = data.split(",");
        Motion2  = temp[0];
        Bat2     = temp[1];
        Node2TS  = temp[2];
        //console.log("Node2 = %o : %o : %o",Motion2,Bat2,Node2TS)
    }

    function callNode3Macro(){
        webiopi().callMacro("wsNode3", [], macro_Node3_Callback);
    }
    function macro_Node3_Callback(macro, args, data){
        var temp = data.split(",");
        Temp3  = temp[0];
        Humid3 = temp[1];
        Light3 = temp[2];
        Bat3   = temp[3];
        Node3TS  = temp[4];
        // console.log("Node3 = %o : %o : %o : %o : %o",Temp3,Humid3,Light3,Bat3,Node3TS)
    }

    function callNode4Macro(){
        webiopi().callMacro("wsNode4", [], macro_Node4_Callback);
    }
    function macro_Node4_Callback(macro, args, data){
        var temp = data.split(",");
        Temp4  = temp[0];
        Humid4 = temp[1];
        Light4 = temp[2];
        Bat4   = temp[3];
        Node4TS  = temp[4];
        // console.log("Node4 = %o : %o : %o : %o : %o",Temp4,Humid4,Light4,Bat4,Node4TS)
    }

    setInterval (callMailMacro, 6000);
    setInterval (callNode2Macro, 6000);
    setInterval (callNode3Macro, 6000);
    setInterval (callNode4Macro, 6000);

    // Change webiopi generated buttons to bootstrap style

    // var testButton = $("#gpio4").clone();
    // $("#controls").append(testButton);
    // $('button').addClass('btn btn-danger');  

    //$('#gpio4').removeClass('button').addClass('btn btn-danger');  
    // alert( "ready!" );

    // Refresh GPIO buttons
    // pass true to refresh repeatedly of false to refresh once
    webiopi().refreshGPIO(true);

    // Setup gauges

    // ******* Node 2 *********
    var m2_1 = new JustGage({
        id: "gauge_m2_1",
        value: Motion2,
        min: 0,
        max: 1,
        donut: true,
        label: 'test',
        relativeGaugeSize: true,
        title: "Motion Detect"
    });

    var m2_2 = new JustGage({
        id: "gauge_m2_4",
        value: Bat2,
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

    // ******* Node 3 *********
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
        value: Light3,
        min: 0,
        max: 1000,
        symbol: '',
        relativeGaugeSize: true,
        title: "Light Level"
    });

    var t3_4 = new JustGage({
        id: "gauge_t3_4",
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

    // ******* Node 4 *********
    var t4_1 = new JustGage({
        id: "gauge_t4_1",
        value: Temp4,
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

    var t4_2 = new JustGage({
        id: "gauge_t4_2",
        value: Humid4,
        min: 0,
        max: 100,
        symbol: '%',
        relativeGaugeSize: true,
        title: "Humidity"
    });

    var t4_3 = new JustGage({
        id: "gauge_t4_3",
        value: Light4,
        min: 0,
        max: 1000,
        symbol: '',
        relativeGaugeSize: true,
        title: "Light Level"
    });

    var t4_4 = new JustGage({
        id: "gauge_t4_4",
        value: Bat4,
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

    // Update info periodically
    setInterval(function() {
        m2_1.refresh(Motion2);
        m2_2.refresh(Bat2);
        document.getElementById("m2_time").innerText=Node2TS;

        t3_1.refresh(Temp3);
        t3_2.refresh(Humid3);
        t3_3.refresh(Light3);
        t3_4.refresh(Bat3);
        document.getElementById("t3_time").innerText=Node3TS;

        t4_1.refresh(Temp4);
        t4_2.refresh(Humid4);
        t4_3.refresh(Light4);
        t4_4.refresh(Bat4);
        document.getElementById("t4_time").innerText=Node4TS;

        e1.refresh(UnreadCnt);
        document.getElementById("email_2_subject").innerText=Subject;
    }, 6000);

});

