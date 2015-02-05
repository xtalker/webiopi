
webiopi().ready(function() {

    // Globals
    var UnreadCnt = 0;
    var Temp3 = 0;
    
    // Create a button to call setLightHours macro
    var sendButton = webiopi().createButton("testButton", "Test", function() {
        document.getElementById("TestLabel").innerText="Done!";
    });

    var mailCntbutton = webiopi().createButton("mailCnt", "Count", callMailMacro);
    var mailSubjbutton = webiopi().createButton("mailSubj", "Subject", callMailMacro);
    // Create led buttons
    var button3 = webiopi().createGPIOButton(17, "No Mail");
    var button4 = webiopi().createGPIOButton(9, "Mail");
    var button5 = webiopi().createGPIOButton(22, "Heartbeat");
    var button1 = webiopi().createGPIOButton(4, "Red1");
    var button2 = webiopi().createGPIOButton(10, "Checking");

    // Append the button to the controls box using a jQuery function
    $("#controls").append(sendButton);
    $("#controls").append(mailCntbutton);
    $("#controls").append(mailSubjbutton);
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
    }

    function callTemp3Macro(){
        webiopi().callMacro("wsTemp3", [], macro_Temp3_Callback);
    }

    function macro_Temp3_Callback(macro, args, data){
        var temp = data.split(",");
        Temp3 = temp[0];
        Humid3 = temp[1];
        Bat3 = temp[2];
        //console.log("Temp3 = %o : %o : %o",Temp3,Humid3,Bat3)
    }

    setInterval (callMailMacro, 6000);
    setInterval (callTemp3Macro, 6000);

    // Refresh GPIO buttons
    // pass true to refresh repeatedly of false to refresh once
    webiopi().refreshGPIO(true);


    // Google gauge
    // https://developers.google.com/chart/interactive/docs/gallery/gauge
    //google.setOnLoadCallback(drawChart);
    $(document).ready(drawChart);

      function drawChart() {

        var data = google.visualization.arrayToDataTable([
          ['Label', 'Value'],
          ['Unread Mail', 0],
          ['Humidity', 0],
          ['Battery', 0],
        ]);

        var tempData = google.visualization.arrayToDataTable([
          ['Label', 'Value'],
          ['Temperature', Temp3],
        ]);
          
        var options = {
          min: 0, max: 100, width: 500, height: 200, redFrom: 90, redTo: 100,
          yellowFrom:75, yellowTo: 90, minorTicks: 10
        };

        var tempOptions = {
          min: 50, max: 85, width: 475, height: 175, redFrom: 80, redTo: 85,
          yellowFrom: 60, yellowTo: 80, greenFrom: 50, greenTo: 60, minorTicks: 10
        };

        var meter = new google.visualization.Gauge(document.getElementById('chart_div1'));
        var tempMeter = new google.visualization.Gauge(document.getElementById('chart_div2'));

        meter.draw(data, options);
        tempMeter.draw(tempData, tempOptions);

        setInterval(function() {
          data.setValue(0, 1, UnreadCnt);
          data.setValue(1, 1, Humid3);
          data.setValue(2, 1, Bat3);
          meter.draw(data, options);
        }, 6000);

        setInterval(function() {
          tempData.setValue(0, 1, Temp3);
          tempMeter.draw(tempData, tempOptions);
        }, 6000);

    }

});
