// Start the WebSocket connection
/* global oTran */
oTran.connectWS();

// Clear button
document.querySelector('#btn-clear-log').onclick = () => {
  // Clear the log and anything that was typed so far in the input
  document.querySelector('#json').value = '';
};

// Disconnect button
document.querySelector('#disconnect').onclick = () => {
  console.log(oTran.webSocket);
  if (oTran.webSocket.readyState === WebSocket.OPEN) {
    oTran.webSocket.close();
    document.querySelector('#disconnect').value = 'Connect';
  } else {
    oTran.connectWS();
    document.querySelector('#disconnect').value = 'Disconnect';
  }
};
