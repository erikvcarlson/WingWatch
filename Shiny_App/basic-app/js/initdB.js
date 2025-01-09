let db; 
const request = window.indexedDB.open("StationInformation", 1); // Name, Version Number

request.onerror = (event) => {
    console.error("Why didn't you allow my web app to use IndexedDB?!");
  };
  request.onsuccess = (event) => {
    db = event.target.result;
  };