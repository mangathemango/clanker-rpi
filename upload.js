const fs = require('fs')




url = "http://100.71.55.8:8000"

const updateConfig = async () => {
    try {
        const configData = fs.readFileSync('./actions.py').toString()

        const postResponse = await fetch(url + "/updateActionScript", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ "actionScript": configData })
        })

        console.log(postResponse)
    } catch (error) {
        console.error("Error reading actions.py", error)
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


