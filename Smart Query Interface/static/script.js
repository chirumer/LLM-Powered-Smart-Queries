const url = "/api/sessions";

let sessionId = null;
let newSession = false;
let prevSession = false;

const sidebar = document.querySelector("#sidebar");
const hide_sidebar = document.querySelector(".hide-sidebar");
const new_chat_button = document.querySelector(".new-chat");
const user_menu = document.querySelector(".user-menu ul");
const show_user_menu = document.querySelector(".user-menu button");
let submitButton = document.getElementById("send-button");
const models = document.querySelectorAll(".model-selector button");
const message_box = document.querySelector("#message");
let conversationsElement = document.getElementById("conversations")
let chatContainer = document.getElementById("chat-container");
let msg = document.getElementById('message')


function show_view(view_selector) {
    document.querySelectorAll(".view").forEach(view => {
        view.style.display = "none";
    });

    document.querySelector(view_selector).style.display = "flex";
}


/*-----event listeners------*/

submitButton.addEventListener("click", getMessage)

hide_sidebar.addEventListener("click", function() {
    sidebar.classList.toggle("hidden");
});

msg.addEventListener('keydown', function (event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        document.getElementById('send-button').click();
    }
});


show_user_menu.addEventListener("click", function() {
    if (user_menu.classList.contains("show")) {
        user_menu.classList.toggle("show");
        setTimeout(function() {
            user_menu.classList.toggle("show-animate");
        }, 200);
    } else {
        user_menu.classList.toggle("show-animate");
        setTimeout(function() {
            user_menu.classList.toggle("show");
        }, 50);
    }
});


for (const model of models) {
    model.addEventListener("click", function() {
        document.querySelector(".model-selector button.selected")?.classList.remove("selected");
        model.classList.add("selected");
    });
}


message_box.addEventListener("keyup", function() {
    message_box.style.height = "auto";
    let height = message_box.scrollHeight + 2;
    if (height > 200) {
        height = 200;
    }
    message_box.style.height = height + "px";
});


new_chat_button.addEventListener("click", function() {
      sessionId = null;
      newSession = false;
      prevSession = false;
    show_view(".new-chat-view");
});

document.querySelectorAll(".conversation-button").forEach(button => {
    button.addEventListener("click", function() {
        show_view(".conversation-view");
    });
});


document.addEventListener('DOMContentLoaded', () => {
    const envSelect = document.getElementById('envValue');
    const dbSelect = document.getElementById('databaseValue');
    const modelSelect = document.getElementById('modelValue');

    fetchEnvironment();
    fetchModels();

    envSelect.addEventListener('change', async function() {
        const selectedEnv = this.value;
        if (selectedEnv) {
            try {
                const databases = await fetchDatabases(selectedEnv);
                displayDatabases(databases, dbSelect);
            } catch (error) {
                console.error('Error fetching databases:', error);
            }
        } else {
            // Reset database dropdown if environment is not selected
            dbSelect.innerHTML = '<option value="">Database</option>';
            dbSelect.disabled = true;
        }
    });
});


/*------fetch methods-----*/

async function fetchEnvironment() {
    try {
        const response = await fetch('http://127.0.0.1:5600/api/environments');
        const data = await response.json();
        displayEnvironment(data.environments);
    } catch (error) {
        console.error(error);
    }
}

async function fetchModels() {
    try {
        const response = await fetch('http://127.0.0.1:5600/api/available_models');
        const data = await response.json();
        displayModels(data.available_models);
    } catch (error) {
        console.error(error);
    }
}

async function fetchDatabases(environment) {
    try {
        const response = await fetch(`http://127.0.0.1:5600/api/databases/${environment}`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error(error);
    }
}

/*------display methods-----*/

function displayEnvironment(environments) {
    const envSelect = document.getElementById('envValue');
    envSelect.innerHTML = '<option value="">Environment</option>';

    environments.forEach(env => {
        const option = document.createElement('option');
        option.value = env;
        option.textContent = env.replace("_", " ");
        envSelect.appendChild(option);
    });
}

function displayModels(models) {
    const modelSelect = document.getElementById('modelValue');
    modelSelect.innerHTML = '<option value="">Model</option>';

    models.forEach(model => {
        const option = document.createElement('option');
        option.value = model;
        option.textContent = model;
        modelSelect.appendChild(option);
    });
}

function displayDatabases(databases, dbSelect) {
    dbSelect.innerHTML = '<option value="">Database</option>';
    dbSelect.disabled = false;

    databases.forEach(db => {
        const option = document.createElement('option');
        option.value = db;
        option.textContent = db.replace("_", " ");
        dbSelect.appendChild(option);
    });
}

function displayHistory(data) {
    conversationsElement.innerHTML = null;
    for (let i = data.length - 1; i >= 0; i--) {
        const li = document.createElement('li');
        // Create the button element with the conversation title
        const button = document.createElement('button');
        button.classList.add('conversation-button');
        button.innerHTML = '<i class="fa fa-message fa-regular"></i> ' + data[i].session_title;
        button.addEventListener("click", function () {
            show_view(".conversation-view");
            newSession = false;
            let activeElements = document.getElementsByClassName("active");
            let activeArray = Array.from(activeElements);
            activeArray.forEach(function (element) {
                element.classList.remove("active");
            });
            li.classList.add('active');
            sessionId = data[i].sessionId;
            getSession()
            prevSession=true;
        })
        const fadeDiv = document.createElement('div');
        fadeDiv.classList.add('fade');
        const editButtonsDiv = document.createElement('div');
        editButtonsDiv.classList.add('edit-buttons');
        const editButton = document.createElement('button');
        editButton.innerHTML = '<i class="fa fa-edit"></i>';
        const deleteButton = document.createElement('button');
        deleteButton.innerHTML = '<i class="fa fa-trash"></i>';
        editButtonsDiv.appendChild(editButton);
        editButtonsDiv.appendChild(deleteButton);
        li.appendChild(button);
        li.appendChild(fadeDiv);
        li.appendChild(editButtonsDiv);
        conversationsElement.appendChild(li);
    }
}


function displayChat(data) {
    chatContainer.innerHTML = null
    for (let i = 0; i < data.length; i += 2) {
        appendQuestion(data[i].content);
        appendAnswer(data[i + 1].content, data[i + 1].metadata);
    }
}

/*-------------*/

async function getMessage() {
    const selected_Database = document.getElementById('databaseValue').value;
    const selected_Env = document.getElementById('envValue').value;
    const selected_Model = document.getElementById('modelValue').value;
    if ((selected_Database && selected_Env)||prevSession) {

        if (!selected_Model && !prevSession) {
            alert("Please Select Model")
            return;
        }

        const inputElement = document.getElementById("message");
        let inputValue = inputElement.value.trim();
        if (!inputValue) return;
        if (sessionId == null) newSession = true;
        if (newSession === true) {
            if (await createSession()) {
                sessionId += 1;
            }
            // make the conversation button active
            let conversationButtons = document.getElementsByClassName("conversation-button");
            let conversationArray = Array.from(conversationButtons);
            conversationArray[0].parentElement.classList.add("active");

            // change title 
            conversationArray[0].innerHTML = '<i class="fa fa-message fa-regular"></i> ' + inputValue;
        }
        inputElement.value = "";
        appendQuestion(inputValue);
        try {
            let response = await updateQuestions(inputValue);
            appendAnswer(response.answer, response.metadata);
        } catch (error) {
            console.error('Error occurred:', error);
        }
    } else {
        alert("Please Select Environment or Database.")
    }
}


/*-------Session Methods------*/

async function getSession() {
    try {
        const response = await fetch(`${url}/${sessionId}`);
        const data = await response.json();
        const conversationArray = JSON.parse(data.conversation);
        let databaseTitleElement = document.getElementById('database-title');
        databaseTitleElement.innerHTML = 
        '<i class="fa-solid fa-code" style="margin-right: 3px;"></i> <span style="margin-right: 25px;">' + data.environment + '</span>' + 
        '<i class="fa-solid fa-database" style="margin-right: 3px;"></i> <span style="margin-right: 25px;">' + data.databaseName + '</span>' + 
        '<i class="fa-solid fa-robot" style="margin-right: 3px;"></i> <span style="margin-right: 25px;">' + data.model_name + '</span>';    
        displayChat(conversationArray);
    } catch (error) {
        console.error(error)
    }
}


async function createSession() {
    let envElement = document.getElementById('envValue');
    let environment = envElement.value;
    let dataElement = document.getElementById('databaseValue');
    let databaseName = dataElement.value;
    let modelElement = document.getElementById('modelValue');
    let model = modelElement.value;
    show_view(".conversation-view");
    try {
        const data = {
            "Environment": environment,
            "DatabaseName": databaseName,
            "Model": model
        };
        console.log("Environment: ", data)
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        if (response.ok) {
            const result = await response.json();
            sessionId = result.sessionId;
            await allSession();
            await getSession();
            newSession = false;
        } else console.error('Failed to create session:', response.status);

    } catch (error) {
        console.error('Error:', error);
    }
}


async function allSession() {
    try {
        const response = await fetch(url);
        const data = await response.json();
        displayHistory(data)
    } catch (error) {
        console.error(error)
    }
}
allSession()


/*----async methods-------*/

async function updateQuestions(newRequest) {
    let requestBody = {
        "question": newRequest
    }
    try {
        const response = await fetch(`${url}/${sessionId}/question`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });
        const result = await response.json();
        return result;
    } catch (error) {
        console.error('Error:', error);
    }
}


async function updateAnswers(newRequest) {
    let requestBody = {
        "answer": newRequest
    }
    try {
        const response = await fetch(`${url}/${sessionId}/answer`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });
        const result = await response.json();
        if (result) {
            getSession();
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

/*----append methods-------*/

function appendQuestion(question) {
    // Create and append the user message
    const userMessageDiv = document.createElement('div');
    userMessageDiv.classList.add('user', 'message');

    const identityDiv = document.createElement('div');
    identityDiv.classList.add('identity');
    const userIcon = document.createElement('i');
    userIcon.classList.add('user-icon');
    userIcon.textContent = 'u';
    identityDiv.appendChild(userIcon);

    const contentDiv = document.createElement('div');
    contentDiv.classList.add('content');
    const messageParagraph = document.createElement('p');
    messageParagraph.textContent = question;
    contentDiv.appendChild(messageParagraph);

    userMessageDiv.appendChild(identityDiv);
    userMessageDiv.appendChild(contentDiv);

    chatContainer.appendChild(userMessageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function appendAnswer(answer, metadata) {
    const assistantMessageDiv = document.createElement('div');
    assistantMessageDiv.classList.add('assistant', 'message');
    assistantMessageDiv.style.position = 'relative'; // Ensure the parent has relative positioning

    const assistantIdentityDiv = document.createElement('div');
    assistantIdentityDiv.classList.add('identity');
    const assistantIcon = document.createElement('i');
    assistantIcon.classList.add('gpt', 'user-icon');
    assistantIcon.textContent = 'H';
    assistantIdentityDiv.appendChild(assistantIcon);

    const assistantContentDiv = document.createElement('div');
    assistantContentDiv.classList.add('content');
    const assistantMessageParagraph = document.createElement('p');
    assistantMessageParagraph.innerHTML = answer;
    assistantContentDiv.appendChild(assistantMessageParagraph);

    let tooltipDiv = document.createElement("div");
    tooltipDiv.classList.add("tooltipDiv");

    if (metadata) {
        const metadata_lines = metadata.split('|');
        metadata_lines.forEach(line => {
            const tooltip = document.createElement('p');
            tooltip.textContent = line;
            tooltip.classList.add("tooltip");
            tooltipDiv.appendChild(tooltip);
        });
    }

    assistantMessageDiv.addEventListener('mouseover', function () {
        tooltipDiv.style.display = 'block';
    });

    assistantMessageDiv.addEventListener('mouseout', function () {
        tooltipDiv.style.display = 'none';
    });

    assistantMessageDiv.appendChild(assistantIdentityDiv);
    assistantMessageDiv.appendChild(assistantContentDiv);
    assistantContentDiv.appendChild(tooltipDiv); // Append tooltip within the content div

    chatContainer.appendChild(assistantMessageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}
