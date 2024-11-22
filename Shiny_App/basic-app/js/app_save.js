// Function to fetch and save pkl files to LocalStorage
async function savePklFilesToLocalStorage(fileName) {
    // Using Fetch API (modern browsers)
    fetch(`${fileName}`)
        .then(response => response.json())
        .then(data => {
            // Do something with the JSON data
            console.log(data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Example Usage

savePklFilesToLocalStorage("5501/Station1.json");

alert("If you're seeing this, the javascript file was included successfully.");

// Example Usage
//const fileNames = ["file1.pkl", "file2.pkl", "file3.pkl"];

// Save files to LocalStorage


// Retrieve and download a file
// downloadPklFromLocalStorage("file1.pkl");
