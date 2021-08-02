// Start the WebSocket connection
oTran.connectWS();

// Clear button
document.querySelector('#btn-clear-log').onclick = function (e) {
    // Clear the log and anything that was typed so far in the input
    document.querySelector('#json').value = '';
};

// Disconnect button
document.querySelector('#disconnect').onclick = function (e) {
    console.log(oTran.webSocket);
    if (oTran.webSocket.readyState === WebSocket.OPEN) {
        oTran.webSocket.close();
        //oTran.webSocket = null;
        this.value = "Connect";
    } else {
        oTran.connectWS();
        this.value = "Disconnect";
    }
};
