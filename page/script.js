const img = document.getElementById("cam");

url = "http://127.0.0.1:8000"

async function update() {
    const res = await fetch(url + "/frame");
    const blob = await res.blob();
    img.src = URL.createObjectURL(blob);
    console.log("Fetched stuff")
}

const setArmMotorPositionUp = () => {
    console.log("Upping it")
    sendRequest("/setArmMotorPositionUp")
}
const setArmMotorPositionDown = () => {
    console.log("Downing it")
    sendRequest("/setArmMotorPositionDown")
}
const resetArmMotorPosition = () => {
    console.log("Resetting it")
    sendRequest("/resetArmMotorPosition")

}

const sendRequest = (endpoint) => {
    fetch(url + endpoint, {
        method: "POST"
    })
    .then(res => {
        console.log(res)
    })
}

const openClaw = () => {
    console.log("Resetting it")
    fetch(url, {
        method: "POST"
    })
    .then(res => {
        console.log(res)
    })
}

const updateConfig = () => {
    fetch(url + "/updateConfig", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ "config": document.getElementById("config-json").value })
    })
    .then(res => {
        console.log(res)
    })
}

const executeActions = () => {
    sendRequest("/executeActions")
}