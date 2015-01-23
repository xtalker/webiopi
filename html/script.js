//<script type="text/javascript">

webiopi().ready(function() {

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
    }

    setInterval (callMailMacro, 6000);

    // Refresh GPIO buttons
    // pass true to refresh repeatedly of false to refresh once
    webiopi().refreshGPIO(true);
});
        
//</script>
