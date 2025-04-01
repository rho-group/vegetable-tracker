import { useState, useEffect } from "react";

export default function FoodTracker() {
  const [food, setFood] = useState("");
  const [foods, setFoods] = useState([]);

  const addFood = async () => {
    await fetch("http://your_backend_server_ip/add_food/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: 1, food_name: food }),
    });
    setFood("");
    fetchFoods();
  };

  const fetchFoods = async () => {
    const response = await fetch(`http://your_backend_server_ip/recent_foods/?user_id=1`);
    const data = await response.json();
    setFoods(data.recent_foods);
  };

  useEffect(() => {
    fetchFoods();
  }, []);

  return (
    <div>
      <h2>Food Tracker</h2>
      <input value={food} onChange={(e) => setFood(e.target.value)} />
      <button onClick={addFood}>Add Food</button>
      <h3>Last 7 Days:</h3>
      <ul>
        {foods.map((item, index) => (
          <li key={index}>{item}</li>
        ))}
      </ul>
    </div>
  );
}
