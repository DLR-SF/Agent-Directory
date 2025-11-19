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
function execute_function(eventOrForm, idShort, endpoint) {
    // eventOrForm: can be an Event (from addEventListener) or the FORM element (when called from inline onsubmit)
    let event = null;
    let form = null;

    if (eventOrForm && eventOrForm.tagName === 'FORM') {
        // called as execute_function(this, ...)
        form = eventOrForm;
    } else if (eventOrForm && typeof eventOrForm.preventDefault === 'function') {
        // called with an Event
        event = eventOrForm;
        form = event.target;
        if (form && form.tagName !== 'FORM' && form.closest) {
            form = form.closest('form') || form;
        }
        try { event.preventDefault(); } catch (e) { /* ignore */ }
    } else {
        // fallback: try to find a form near the active element
        const ae = document.activeElement;
        form = (ae && typeof ae.closest === 'function') ? ae.closest('form') : document.querySelector('form');
    }

    // Read raw input (assumes a form field named `input_vars` on the form)
    let raw = '';
    try {
        if (form && typeof FormData !== 'undefined') {
            const fd = new FormData(form);
            raw = fd.get('input_vars') || '';
        }
        if ((!raw || raw === 'null') && form && form.querySelector) {
            const ta = form.querySelector('[name="input_vars"]');
            if (ta) raw = ta.value || '';
        }
    } catch (e) {
        raw = '';
    }

    // Try to parse JSON; if it fails send it wrapped in an object
    let inputVarsObj;
    try {
        inputVarsObj = JSON.parse(raw);
    } catch (e) {
        inputVarsObj = { value: raw };
    }

    // Prepare payload and send CORS request directly from the browser to the target service
    // Some backend handlers expect the JSON root to be { "inputVariables": ... } —
    // wrap automatically if we don't already have that shape.
    let payload = inputVarsObj;
    if (payload && typeof payload === 'object' && !Array.isArray(payload) && !Object.prototype.hasOwnProperty.call(payload, 'inputVariables')) {
        payload = { inputVariables: payload };
    }

    // Build direct target URL from the endpoint value (endpoint may be "host:port" or a full URL)
    let base = endpoint || '';
    if (!/^https?:\/\//i.test(base)) {
        base = 'http://' + base;
    }
    // remove trailing slashes
    base = base.replace(/\/+$/g, '');
    const url = base + '/agent-capabilities/' + encodeURIComponent(idShort);

    // Send CORS request directly from the browser to the target service
    fetch(url, {
        method: 'POST',
        body: JSON.stringify(payload),
        mode: 'cors',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Endpoint': endpoint
        }
    })
    .then(async (response) => {
        const text = await response.text();
        let message, result;
        if (!response.ok) {
            // request sent, but failed
            message = 'Capability execution failed (' + response.status + '). Response: ' + text;
            result = 'error';
        } else {
            // request sent and success
            message = 'Capability successfully executed (' + response.status + '). Response: ' + text;
            result = 'success';
        }
        showAlert(message, result);
    })
    .catch((error) => {
        // request not sent because of issue
        const message = "Can't execute capability. Error: '" + error + "'";
        showAlert(message, 'error');
    });
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