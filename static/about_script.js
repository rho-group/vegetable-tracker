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
                fetch(`/get_vegetables_with_vitamin?vitamin=${vitamin}`)
                    .then(response => response.json())
                    .then(data => {
                        infoBox.innerHTML = `
                            <strong>${vitamin_names[vitamin]}</strong> from these:
                            <ul>${data.map(item => `<li>${item}</li>`).join('')}</ul>
                        `;
                    });
            });

            container.appendChild(box);
        });
    }
});