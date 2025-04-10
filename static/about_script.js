const button = document.getElementById("load-btn");
const textBox = document.getElementById("veggie-list");

button.addEventListener("click", () => {
  // Toggle the textBox visibility
  if (textBox.style.display === "none" || textBox.style.display === "") {
    textBox.style.display = "block";

    button.classList.remove("default");
    button.classList.add("selected");

    fetch("/in_season")  
      .then(response => {
        console.log("Response received:", response);  // Log the response object
        return response.json();
      })
      .then(data => {
        console.log("Parsed data:", data);  // Log the parsed data

        // Check if data.in_season exists and is an array
        if (!data.in_season || !Array.isArray(data.in_season)) {
          console.error("Invalid data format:", data);
          textBox.innerHTML = "<p>Error: Invalid data format or empty data</p>";
          return;
        }

        textBox.innerHTML = "";  // Clear any previous content

        if (data.in_season.length === 0) {
          textBox.innerHTML = "<p>No vegetables in season right now</p>";
        } else {
          // Loop through the in_season array and display each vegetable
          data.in_season.forEach(veg => {
            const item = document.createElement("div");
            item.classList.add("veggie-item");
            item.textContent = `${veg.name}`;
            textBox.appendChild(item);
          });
        }
      })
      .catch(error => {
        console.error("Error fetching data:", error);
        textBox.innerHTML = "<p>Error loading veggies</p>";
      });
  } else {
    textBox.style.display = "none";

    button.classList.remove("selected");
    button.classList.add("default");
  }
});


document.addEventListener("DOMContentLoaded", () => {
    const vitamin_names = {
        calsium: "calsium", carotenoids: "carotenoids", iron: "iron", fiber: "fiber",
        folate: "folate", iodine: "iodine", kalium: "kalium", magnesium: "magnesium",
        niacin: "niacin", phosphorus: "phosphorus", riboflavin: "riboflavin", selenium: "selenium",
        thiamin: "thiamin", vitamina: "vitamin A", vitaminb12: "vitamin B12",
        vitaminc: "vitamin C", vitamind: "vitamin D", vitamink: "vitamin K",
        vitaminb6: "vitamin B6", zinc: "zinc"
    };

    const container = document.getElementById("vitamin-click-container");
    const infoBox = document.getElementById("vitamin-info-box");

    if (container && infoBox) {
        Object.keys(vitamin_names).forEach(vitamin => {
            const box = document.createElement('div');
            box.className = 'box2 m-1 p-2 border border-success rounded';
            box.textContent = vitamin_names[vitamin];
            box.style.cursor = "pointer";

            box.addEventListener('click', () => {
                // remove selected from other
                container.querySelectorAll('.box2').forEach(b => b.classList.remove('selected'));
            
                // add 'selected' clicked box
                box.classList.add('selected');
            
                // Fetch 
                fetch(`/get_vegetables_with_vitamin?vitamin=${vitamin}`)
                    .then(response => response.json())
                    .then(data => {
                        infoBox.innerHTML = `
                            <strong>${vitamin_names[vitamin].charAt(0).toUpperCase() + vitamin_names[vitamin].slice(1)}</strong> from these:
                            <ul>${data.map(item => `<li>${item}</li>`).join('')}</ul>
                        `;
                    });
            });

            container.appendChild(box);
        });
    }
});