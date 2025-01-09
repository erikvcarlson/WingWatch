// writeToDB.js

function writeToIndexedDB(db, storeName, data) {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(storeName, 'readwrite');
        const store = transaction.objectStore(storeName);

        const request = store.add(data);

        request.onsuccess = function (event) {
            console.log("Data written successfully:", event.target.result);
            resolve(event.target.result); // Returns the generated key
        };

        request.onerror = function (event) {
            console.error("Error writing data:", event.target.errorCode);
            reject(event.target.errorCode); // Reject with error
        };
    });
}

// Example usage:
const dbName = "UserInformation";
const version = 1;
const storeName = "Stations";

// Call initializeDB.js function to initialize DB
window.initializeIndexedDB(dbName, version, storeName)
    .then((db) => {
        // Data to write to the store
        const data = {
            name: StationName,
            lat: latValue,
            long: longValue,
        };

        // Write data to IndexedDB
        return writeToIndexedDB(db, storeName, data);
    })
    .then((key) => {
        console.log("Data written with key:", key);
    })
    .catch((error) => {
        console.error("Failed to initialize or write data:", error);
    });
