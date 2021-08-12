// This is sort of like a class

const oTran = {};

oTran.webSocket = null;
//oTran.roomName = JSON.parse(document.getElementById('room-name').textContent);

// Perform the WS connection
oTran.connectWS = function () {

  const ws_scheme = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
  const endpoint = '/graphql/';

  // https://developer.mozilla.org/en-US/docs/Web/API/WebSocket
  this.webSocket = new WebSocket(
    ws_scheme
    + window.location.host
    + endpoint, 'graphql-ws'
  );
  console.log('host is ' + window.location.host);
  console.log('url is ' + this.webSocket.url);
  console.log('protocol is ' + this.webSocket.protocol);

  this.webSocket.onmessage = oTran.onmessage;
  this.webSocket.onopen = oTran.onopen;
  this.webSocket.onclose = oTran.onclose;
  this.webSocket.onerror = oTran.error;
};

// onMessage event
// This occurs when the Websocket sends back data.
oTran.onmessage = function (e) {

  const data = JSON.parse(e.data);
  console.log(data); // Show the whole data package for debugging

  // Make sure we are who we think we are . . . or something
  console.log('op_id: ' + data.id);

  switch (data.type) {
    // YYZ - ANTHONY - Who set the data type to data? Did I?
    case 'data':
      // If there are errors, let me know right away
      if (data.payload.errors) {
        for (const error of data.payload.errors) {
          console.log(error.message);
        }
        return;
      }

      // Valid payload?
      if (data.payload.data) {

        // Shorthand
        /** @namespace data.onSnippetNoGroup */
        const payload = data.payload.data.onSnippetNoGroup;

        /** @namespace payload.transType */
        console.log('transType: ' + payload.transType);
        console.log('sender: ' + payload.sender);
        console.log('ok?: ' + payload.ok);

        // Access the database object
        /** @namespace payload.snippet */
        document.querySelector('#json').value = '' +
          'Transaction Type: ' + payload.transType + '\n' +
          'Snippet:\n' +
          JSON.stringify(payload.snippet, null, 2);
      } else {
        console.log('Invalid payload');
        return;
      }

      break;
    default:
      console.log('Unknown data.type [' + data.type + ']');
  }
};

// onOpen event
oTran.onopen = function open() {
  console.log('Chat socket opened');

  // See channels_graphql_ws/graphql_ws_consumer.py for what is wanted
  // to start a subscription. Can also look at the unit test.
  let content = {};
  content.id = 1; // A unique sequence? See channels_graphql_ws/graphql_ws_consumer.py:315
  content.type = 'start';
  let payload = {};
  payload.query = String.raw`
subscription subNoGroup {
  onSnippetNoGroup {
    sender
    transType
    ok
    snippet {
      id
      title
      private
      owner
      created
    }
  }
}
    `;
  payload.operationName = 'subNoGroup';
  content.payload = payload;

  let contentJSON = JSON.stringify(content, null, 2);

  // This looks good in the console or in a <textarea>, but it's no longer JSON.
  const contentPrettyJSON = textAreaCleanup(contentJSON);
  console.log('Subscription JSON ' + contentPrettyJSON);
  document.querySelector('#json').value = contentPrettyJSON;

  // Send the JSON to API via the WebSocket
  oTran.webSocket.send(contentJSON);
};

// onClose event
oTran.onclose = function (closeEvent) {
  // console.log(closeEvent);
  if (closeEvent.wasClean) {
    console.log('Chat socket closed, clean close. Code [' + closeEvent.code + ']');
  } else {
    console.error('Chat socket closed, unclean close', closeEvent);
  }
};

// onError event
oTran.onerror = function (event) {
  console.error('Websocket error observed: ', event);
};

function textAreaCleanup(str) {
  return str.replace(/\\n/g, '\r\n');
}

//export default oTran;