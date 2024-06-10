const url = "/api/sessions"

let sessionId = null;
let environment = null;
let databaseName = null
let newSession = false;

const sidebar = document.querySelector("#sidebar");
const hide_sidebar = document.querySelector(".hide-sidebar");
const new_chat_button = document.querySelector(".new-chat");

hide_sidebar.addEventListener("click", function () {
    sidebar.classList.toggle("hidden");
});

const user_menu = document.querySelector(".user-menu ul");
const show_user_menu = document.querySelector(".user-menu button");

show_user_menu.addEventListener("click", function () {
    if (user_menu.classList.contains("show")) {
        user_menu.classList.toggle("show");
        setTimeout(function () {
            user_menu.classList.toggle("show-animate");
        }, 200);
    } else {
        user_menu.classList.toggle("show-animate");
        setTimeout(function () {
            user_menu.classList.toggle("show");
        }, 50);
    }
});

const models = document.querySelectorAll(".model-selector button");

for (const model of models) {
    model.addEventListener("click", function () {
        document.querySelector(".model-selector button.selected")?.classList.remove("selected");
        model.classList.add("selected");
    });
}

const message_box = document.querySelector("#message");

message_box.addEventListener("keyup", function () {
    message_box.style.height = "auto";
    let height = message_box.scrollHeight + 2;
    if (height > 200) {
        height = 200;
    }
    message_box.style.height = height + "px";
});

function show_view(view_selector) {
    document.querySelectorAll(".view").forEach(view => {
        view.style.display = "none";
    });

    document.querySelector(view_selector).style.display = "flex";
}

new_chat_button.addEventListener("click", function () {
    show_view(".new-chat-view");
    newSession = true;
});

document.querySelectorAll(".conversation-button").forEach(button => {
    button.addEventListener("click", function () {
        show_view(".conversation-view");
    })
});
//=====================================================================
async function getMessage() {
    const selected_Database = document.getElementById('databaseValue').value;
    const selected_Env = document.getElementById('envValue').value;
    if (selected_Database && selected_Env) {
        const inputElement = document.getElementById("message");
        let inputValue = inputElement.value.trim();
        if (!inputValue) return;
        if (sessionId == null) newSession = true;
        if (newSession === true) {
            if (await createSession()) {
                sessionId += 1;
            }
        }
        inputElement.value = "";
        appendQuestion(inputValue);
        try {
            let response = await updateQuestions(inputValue);
            setTimeout(() => {
                appendAnswer(response.answer, response.metadata);
            }, 500);
        } catch (error) {
            console.error('Error occurred:', error);
        }
    } else {
        alert("Please Select Enviroment or Database.")
    }
}
//==============================================================================
document.getElementById('message').addEventListener('keydown', function (event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        document.getElementById('sendButton').click();
    }
});
//==============================================================================
async function getSession() {
    try {
        const response = await fetch(`${url}/${sessionId}`);
        const data = await response.json();
        const conversationArray = JSON.parse(data.conversation);
        let databaseTitleElement = document.getElementById('database-title');
        databaseTitleElement.innerHTML = '<i class="fa-solid fa-rocket"></i> ' + data.environment + ",  " + '<i class="fa-solid fa-database"></i> ' + data.databaseName;
        displayChat(conversationArray);
    } catch (error) {
        console.error(error)
    }
}
//==============================================================================
async function createSession() {
    let envElement = document.getElementById('envValue');
    let environment = envElement.value;
    let dataElement = document.getElementById('databaseValue');
    let databaseName = dataElement.value;
    show_view(".conversation-view");
    try {
        const data = {
            "Environment": environment,
            "DatabaseName": databaseName
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
//==============================================================================
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
//==============================================================================
let conversationsElement = document.getElementById("conversations")

function displayHistory(data) {
    conversationsElement.innerHTML = null;
    for (let i = data.length - 1; i >= 0; i--) {
        const li = document.createElement('li');
        // Create the button element with the conversation title
        const button = document.createElement('button');
        button.classList.add('conversation-button');
        button.innerHTML = '<i class="fa fa-message fa-regular"></i> This is a Session ' + data[i].sessionId;
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

//==============================================================================
let chatContainer = document.getElementById("chat-container");

function displayChat(data) {
    chatContainer.innerHTML = null
    for (let i = 0; i < data.length; i += 2) {
        appendQuestion(data[i].content);
        appendAnswer(data[i + 1].content, data[i + 1].metadata);
    }
}
//=====================================================================
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
//=====================================================================
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
//=====================================================================
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
//=====================================================================
function appendAnswer(answer, sqlQuery) {
    //  Create and append the AI generated response
    const assistantMessageDiv = document.createElement('div');
    assistantMessageDiv.classList.add('assistant', 'message');

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

    const tooltip = document.createElement('p');
    tooltip.textContent = sqlQuery;
    tooltip.classList.add("tooltip")
    const tooltip1 = document.createElement('p');
    tooltip1.textContent = sqlQuery;
    tooltip1.classList.add("tooltip")

    tooltipDiv.append(tooltip, tooltip1)

    assistantMessageDiv.addEventListener('mouseover', function (event) {
        const rect = event.target.getBoundingClientRect();
        tooltipDiv.style.display = 'block';
        tooltipDiv.classList.add('show');
    });

    assistantMessageDiv.addEventListener('mouseout', function () {
        tooltipDiv.style.display = 'none';
        tooltipDiv.classList.remove('show');
    });
    assistantMessageDiv.appendChild(assistantIdentityDiv);
    assistantMessageDiv.appendChild(assistantContentDiv);
    chatContainer.appendChild(tooltipDiv);

    chatContainer.appendChild(assistantMessageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}
//=====================================================================
let submitButton = document.getElementById("sendButton");
submitButton.addEventListener("click", getMessage)
//=====================================================================
async function fetchEnvironment() {
    try {
        const response = await fetch('/api/environments');
        const data = await response.json();
        displayEnviroment(data.environments);
    } catch (error) {
        console.error(error)
    }
}
fetchEnvironment()
//=====================================================================
async function fetchDatabases(environment) {
    try {
        const response = await fetch(`/api/databases/${environment}`);
        const data = await response.json();
        console.log("Databases", data)
        return data;
    } catch (error) {
        console.error(error)
    }
}
//=====================================================================
function displayEnviroment(environments) {
    console.log(environments);
    const envSelect = document.getElementById('envValue');
    const dbSelect = document.getElementById('databaseValue');

    environments.forEach(env => {
        const option = document.createElement('option');
        option.value = env;
        option.textContent = env.replace("_", " ");
        envSelect.appendChild(option);
    });

    envSelect.addEventListener('change', function () {
        const selectedEnv = this.value;
        let databasesPromise = fetchDatabases(selectedEnv);

        databasesPromise.then(databases => {
            console.log(databases);
            console.log("databases", databases);
            dbSelect.innerHTML = '<option value=""> Database </option>';
            if (selectedEnv && databases) {
                databases.forEach(db => {
                    const option = document.createElement('option');
                    option.value = db;
                    option.textContent = db.replace("_", " ");
                    dbSelect.appendChild(option);
                });
            }
        }).catch(error => {
            console.error('Error fetching databases:', error);
        });
    });
}
