const fs = require('fs')




url = "http://100.71.55.8:8000"

const updateConfig = async () => {
    try {
        const configData = fs.readFileSync('./config.json').toString()

        const postResponse = await fetch(url + "/updateConfig", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ "config": configData })
        })

        console.log(postResponse)
    } catch (error) {
        console.error("Error reading config.json:", error)
    }
}

const sendRequest = async (endpoint) => {
    await fetch(url + endpoint, {
        method: "POST"
    })
        .then(res => {
            console.log(res)
        })
}

const executeActions = async () => {
    sendRequest("/executeActions")
}

updateConfig().then(() => executeActions())

