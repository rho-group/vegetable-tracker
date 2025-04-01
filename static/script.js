document.addEventListener("DOMContentLoaded", function () {
    const inputField = document.getElementById("inputField");
    const suggestionsList = document.getElementById("suggestions");
    const selectedList = document.getElementById("selected-list");

    // Fetch suggestions when user types
    inputField.addEventListener("input", function () {
        let query = this.value.trim();

        if (query.length === 0) {
            suggestionsList.innerHTML = "";
            return;
        }

        fetch(`/suggest?q=${query}`)
            .then(response => response.json())
            .then(data => {
                suggestionsList.innerHTML = ""; // Clear previous suggestions
                data.forEach(item => {
                    let li = document.createElement("li");
                    li.textContent = item;

                    // Add item to the selected list and update Python list
                    li.onclick = function () {
                        addToList(item);
                        inputField.value = "";
                        suggestionsList.innerHTML = ""; // Clear suggestions after selection
                    };

                    suggestionsList.appendChild(li);
                });
            })
            .catch(error => console.error("Error fetching suggestions:", error));
    });

    // Function to add item to the selected list
    function addToList(item) {
        let li = document.createElement("li");
        li.textContent = item;

        // Remove item from selected list and update Python list
        li.onclick = function () {
            removeFromList(item, li);
        };

        selectedList.appendChild(li);

        // Update the Python list by sending a POST request
        fetch('/add_item', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ item: item })
        });
    }

    // Function to remove item from selected list and Python list
    function removeFromList(item, li) {
        selectedList.removeChild(li);

        // Update the Python list by sending a DELETE request
        fetch('/remove_item', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ item: item })
        });
    }
});
