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
   
    let debounceTimer;
    const debounceDelay = 200;
    
    let selectedItems = [];

    const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

    // Dictionary for creating vitamin intake boxes
    let vitamin_names = {
        calsium:'Calsium',
        carotenoids:'Carotenoids',
        iron:'Iron',
        fiber:'Fiber',
        folate:'Folate',
        iodine:'Iodine',
        kalium:'Kalium',
        magnesium:'Magnesium',
        niacin:'Niacin',
        phosphorus:'Phosphorus',
        riboflavin:'Riboflavin',
        selenium:'Selenium',
        thiamin:'Thiamin',
        vitamina:'Vitamin A',
        vitaminb12:'Vitamin B12',
        vitaminc:'Vitamin C',
        vitamind:'Vitamin D',
        vitamink:'Vitamin K',
        vitaminb6:'Vitamin B6',
        zinc:'Zinc'
    }

    // Create the boxes for vitamins
    Object.keys(vitamin_names).forEach(vitamin => {
        const box = document.createElement('div');
        box.className = 'box';
        box.id = vitamin
        box.textContent = vitamin_names[vitamin];
        vitaminBoxContainer.appendChild(box);
    })

    function refreshVitaminBoxes() {
        const boxes = document.querySelectorAll(".box");
        
        fetch('get_vitamins')
        .then(response => response.json())
        .then(data => {
            boxes.forEach(box => {
                boxId = box.id
                if (data[boxId] === 1) {
                    box.classList.add("green");
                } else {
                    box.classList.remove("green")
                }
          });
          
        })
        
    }

    function refreshChart() {
        barChartImg.src = "/get_bar_chart?" + new Date().getTime(); // Prevent caching
    }

    function toTitleCase(str) {
        return str.replace(/\w\S*/g, text => text.charAt(0).toUpperCase() + text.substring(1).toLowerCase());
    }

    function showEatenList() {
        fetch('/get_items')
        .then(response => response.json())
        .then(data => {
            console.log("Server response for get items function:", data);
            alreadyEatenList.innerHTML = "";
            
            for (let item in data) {
                let li = document.createElement("li");
                li.textContent = toTitleCase(data[item])
                alreadyEatenList.appendChild(li);
            }
        })};
        
    refreshVitaminBoxes()
    showEatenList()

    // Get suggestions when user is typing
    inputField.addEventListener("input", function () {
        let query = this.value.trim();

        clearTimeout(debounceTimer);

        if (query.length === 0) {
            suggestionsList.innerHTML = "";
            return;
        }

        debounceTimer = setTimeout(() => {
            fetch(`/suggest?q=${query}`)
            .then(response => response.json())
            .then(data => {
                suggestionsList.innerHTML = "";
                data.forEach(item => {
                    let li = document.createElement("li");
                    li.classList.add('vitamin-list-item')

                    const veg_str = toTitleCase(item.vegetable)
                    const vit_str = toTitleCase(item.vitamins.join(', '))

                    li.innerHTML = `<b>${veg_str}</b> <span class="vitamin-text">${vit_str}</span>`

                    li.classList.add('dropdown-item')
                    li.onclick = function () {
                        addToList(item.vegetable);
                        inputField.value = "";
                        suggestionsList.innerHTML = "";
                    };
                    suggestionsList.appendChild(li);
                });
            })
            .catch(error => console.error("Error fetching suggestions:", error));
        }, debounceDelay);

        
    });

    // Add vegetable to intermediate list before eating
    function addToList(vegetable) {
        if (!selectedItems.includes(vegetable)) { 
            selectedItems.push(vegetable);

            let li = document.createElement("li");
            
            li.innerHTML = `<span class="list-text">${toTitleCase(vegetable)}<span class="close-button">&times;</span></span>`
            
            li.setAttribute('class','dropdown-item')
            li.onclick = function () {
                removeFromList(vegetable, li);
            };
            selectedList.appendChild(li);
        }
    }

    // Delete vegetable from intermediate list
    function removeFromList(vegetable, li) {
        console.log('Remove from list function called')
        selectedItems = selectedItems.filter(i => i !== vegetable);
        selectedList.removeChild(li);
    }

    // Add vegetable to database (eat it)
    sendButton.addEventListener("click", function () {
        fetch('/save_items', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                items: selectedItems,       
                timezone: userTimezone  // Send the user's local timezone
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log("Server response:", data);
            selectedItems = []; 
            selectedList.innerHTML = ""; 
            alreadyEatenList.innerHTML = "";

            for (let item in data.selected_items) {
                let li = document.createElement("li");
                li.textContent = toTitleCase(data.selected_items[item])

                alreadyEatenList.appendChild(li);
            }
            refreshVitaminBoxes()
            refreshChart();
        })
        .catch(error => console.error("Error sending data:", error));
    });

});
