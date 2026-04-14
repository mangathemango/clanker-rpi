const img = document.getElementById("cam");

async function update() {
    const res = await fetch("http://100.71.55.8:8000/frame");
    const blob = await res.blob();
    img.src = URL.createObjectURL(blob);
    console.log("Fetched stuff")
}

const setArmMotorPositionUp = () => {
    console.log("Upping it")
    sendRequest("setArmMotorPositionUp")
}
const setArmMotorPositionDown = () => {
    console.log("Downing it")
    sendRequest("setArmMotorPositionDown")
}
const resetArmMotorPosition = () => {
    console.log("Resetting it")
    sendRequest("resetArmMotorPosition")

}

const sendRequest = (endpoint) => {
    fetch("http://100.71.55.8:8000/" + endpoint, {
        method: "POST"
    })
    .then(res => {
        console.log(res)
    })
}

const openClaw = () => {
    console.log("Resetting it")
    fetch("http://100.71.55.8:8000/", {
        method: "POST"
    })
    .then(res => {
        console.log(res)
    })
}
