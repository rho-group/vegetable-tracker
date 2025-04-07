document.addEventListener("DOMContentLoaded", function () {
    const inputField = document.getElementById("inputField");
    const suggestionsList = document.getElementById("suggestions");
    const selectedList = document.getElementById("selected-list");
    const alreadyEatenList = document.getElementById("already-eaten-list")
    alreadyEatenList.innerText = ""
    alreadyEatenList.innerHTML = ""
    const barChartImg = document.getElementById("barChart");
    const sendButton = document.getElementById("eat-me-button");
    const vitaminBoxContainer = document.getElementById("vitamin-box-container");

    // Dictionary for vitamin boxes
    let vitamins = {
        ca:1,
        carotens:0,
        fe:0,
        fibc:0,
        fol:0,
        jodi:0,
        k:0,
        mg:0,
        niaeq:0,
        p:0,
        ribf:0,
        se:0,
        thia:0,
        vita:0,
        vitb12:0,
        vitc:0,
        vitd:0,
        vite:0,
        vitpyrid:0,
        zn:0
    }
    
    Object.keys(vitamins).forEach(vitamin => {
        const box = document.createElement('div');
        box.className = 'box';
        box.textContent = vitamin;
        vitaminBoxContainer.appendChild(box);
    })

    let selectedItems = []; // Väliaikainen lista

    function refreshChart() {
        barChartImg.src = "/get_bar_chart?" + new Date().getTime(); // Prevent caching
    }

    function showEatenList() {
        fetch('/get_items')
        .then(response => response.json())
        .then(data => {
            console.log("Server response for get items function:", data);
            alreadyEatenList.innerHTML = "";
            
            for (let item in data) {
                let li = document.createElement("li");
                li.innerHTML = data[item];

                alreadyEatenList.appendChild(li);
            }
    })};

    showEatenList()

    // Ehdotusten haku, kun käyttäjä kirjoittaa
    inputField.addEventListener("input", function () {
        let query = this.value.trim();

        if (query.length === 0) {
            suggestionsList.innerHTML = "";
            return;
        }

        fetch(`/suggest?q=${query}`)
            .then(response => response.json())
            .then(data => {
                suggestionsList.innerHTML = "";
                data.forEach(item => {
                    let li = document.createElement("li");
                    li.textContent = item;
                    li.setAttribute('class','dropdown-item')
                    li.onclick = function () {
                        addToList(item);
                        inputField.value = "";
                        suggestionsList.innerHTML = "";
                    };
                    suggestionsList.appendChild(li);
                });
            })
            .catch(error => console.error("Error fetching suggestions:", error));
    });

    // Lisää valittu ruoka väliaikaiseen listaan
    function addToList(item) {
        console.log('AddToList -function called')
        if (!selectedItems.includes(item)) { // Estää duplikaatit
            selectedItems.push(item);

            let li = document.createElement("li");
            li.textContent = item;
            li.setAttribute('class','dropdown-item')
            li.onclick = function () {
                removeFromList(item, li);
            };
            selectedList.appendChild(li);
        }
    }

    // Poista ruoka väliaikaisesta listasta
    function removeFromList(item, li) {
        console.log('Remove from list function called')
        selectedItems = selectedItems.filter(i => i !== item);
        selectedList.removeChild(li);
    }

    // Lähetä lista Pythonille
    sendButton.addEventListener("click", function () {
        fetch('/save_items', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ items: selectedItems })
        })
        .then(response => response.json())
        .then(data => {
            console.log("Server response:", data);
            selectedItems = []; // Tyhjennetään lista lähetysten jälkeen
            selectedList.innerHTML = ""; // Tyhjennetään UI
            alreadyEatenList.innerHTML = "";

            for (let item in data.selected_items) {
                let li = document.createElement("li");
                li.innerHTML = data.selected_items[item];

                alreadyEatenList.appendChild(li);
            }
        
            refreshChart();
        })
        .catch(error => console.error("Error sending data:", error));
    });

    // Function to check the vitamin boxes
    sendButton.addEventListener("click", function() {
        const boxes = document.querySelectorAll(".box");

        boxes.forEach(box => {
            boxName = box.innerText
            if (vitamins[boxName] === 1) {
                box.classList.add("green");
            } else {
                box.classList.remove("green")
            }
      });
    });
});
