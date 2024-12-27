function initializeIndexedDB(dbName, version, storeName) {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(dbName, version);

        request.onupgradeneeded = function (event) {
            const db = event.target.result;
            if (!db.objectStoreNames.contains(storeName)) {
                db.createObjectStore(storeName, { keyPath: 'id', autoIncrement: true });
                console.log(`Object store '${storeName}' created.`);
            }
        };

        request.onsuccess = function (event) {
            const db = event.target.result;
            console.log(`IndexedDB '${dbName}' initialized successfully.`);
            resolve(db);
        };

        request.onerror = function (event) {
            console.error("Error initializing IndexedDB:", event.target.errorCode);
            reject(event.target.errorCode);
        };
    });
}

// Usage
const dbName = "MyWebAppDB";
const version = 1;
const storeName = "MyStore";

initializeIndexedDB(dbName, version, storeName)
    .then((db) => {
        console.log("Database is ready:", db);
        // Perform further operations with the database
    })
    .catch((error) => {
        console.error("Failed to initialize IndexedDB:", error);
    });
