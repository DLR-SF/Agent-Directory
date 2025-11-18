/**
 * Custom JS
 */

// open ass model details
function openPop(agent_id) {
    const popDialog =
        document.getElementById(
            "popupDialog_" + agent_id
        );
    popDialog.style.visibility =
        popDialog.style.visibility ===
            "visible"
            ? "hidden"
            : "visible";
}

// open action pop up
function openPopAction(model_type, agent_id) {
    var popDialog;
    if (model_type == 'SubmodelElementCapability') {
        popDialog =
            document.getElementById(
                "popupDialog_capabilities_" + agent_id
        );
    } else if (model_type == 'SubmodelElementOperation') {
        popDialog =
            document.getElementById(
                "popupDialog_skills_" + agent_id
        );
    } else {
        popDialog =
            document.getElementById(
                "popupDialog_no_support"
        );
    }

    popDialog.style.visibility =
        popDialog.style.visibility ===
            "visible"
            ? "hidden"
            : "visible";
}

// call agent capability
function execute_function(event, idShort) {
    // Read raw input (assumes a form field named `input_vars` on the form that triggered this)
    let raw = event.target.input_vars.value;

    // Try to parse JSON; if it fails send it wrapped in an object
    let inputVarsObj;
    try {
        inputVarsObj = JSON.parse(raw);
    } catch (e) {
        inputVarsObj = { value: raw };
    }

    // Use a same-origin proxy endpoint so the browser does not have to do cross-origin requests
    const url = '/proxy/agent-capabilities/' + idShort;

    fetch(url, {
        method: "POST",
        body: JSON.stringify(inputVarsObj),
        headers: {
            'Content-Type': 'application/json; charset=UTF-8'
        }
    })
    .then(async (response) => {
        const text = await response.text();
        if (!response.ok) {
            // request send, but no success
            message = 'Capability execution failed (' + response.status + '). Response: ' + text
            result = 'error'
        } else {
            // request send and success
            message = 'Capability successfully executed (' + response.status + '). Response: ' + text
            result = 'success'
        }
    })
    .catch((error) => {
        // request not send because of issue
        message = "Can't execute capability. Error: '" + error + "'"
        result = 'error'
    });
    showAlert(message, result)
}

function showAlert(message, result) {
    // set result text
    document.getElementById("capability_result").textContent=message;

    // set success / failure symbol header
    if (result == 'success') {
        document.getElementById("success-error-image").innerHTML="&#10004;";
        document.getElementById("success-error-image").style.color="#077A26";
    } else {
        document.getElementById("success-error-image").innerHTML="&#10006;";
        document.getElementById("success-error-image").style.color="#A3240B";
    }

    // show alert
    popDialog_alert =
            document.getElementById(
                "capability_exec_alert"
        );

    popDialog_alert.style.visibility = "visible";

}

function closeAlert() {
    // show alert
    popDialog_alert =
            document.getElementById(
                "capability_exec_alert"
        );

    popDialog_alert.style.visibility = "hidden";
}