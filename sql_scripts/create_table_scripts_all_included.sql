DROP TABLE IF EXISTS eaten;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS vegetables;
DROP TABLE IF EXISTS inseason;

CREATE TABLE IF NOT EXISTS users (
	id SERIAL PRIMARY KEY,
	username TEXT,
	password TEXT
);

CREATE TABLE IF NOT EXISTS vegetables (
	id SERIAL PRIMARY KEY,
	foodid TEXT,
	foodname TEXT,
	ca TEXT,
	carotens TEXT,
	fe TEXT,
	fibc TEXT,
	fol TEXT,
	jodi TEXT,
	k TEXT,
	mg TEXT,
	niaeq TEXT,
	p TEXT,
	ribf TEXT,
	se TEXT,
	thia TEXT,
	vita TEXT,
	vitb12 TEXT,
	vitc TEXT,
	vitd TEXT,
	vite TEXT,
	vitk TEXT,
	vitpyrid TEXT,
	zn TEXT,
	Calsium INTEGER,
	Carotenoids INTEGER,
	Iron INTEGER,
	Fiber INTEGER,
	Folate INTEGER,
	Iodine INTEGER,
	Kalium INTEGER,
	Magnesium INTEGER,
	Niacin INTEGER,
	Phosphorus INTEGER,
	Riboflavin INTEGER,
	Selenium INTEGER,
	Thiamin INTEGER,
	VitaminA INTEGER,
	VitaminB12 INTEGER,
	VitaminC INTEGER,
	VitaminD INTEGER,
	VitaminE INTEGER,
	VitaminK INTEGER,
	VitaminB6 INTEGER, 
	Zinc INTEGER	
);

CREATE TABLE IF NOT EXISTS eaten (
	id SERIAL PRIMARY KEY,
	user_id INTEGER,
	veg_id INTEGER,
	date TIMESTAMP,
	CONSTRAINT fk_user
		FOREIGN KEY(user_id)
			REFERENCES users(id),
	CONSTRAINT fk_veg
		FOREIGN KEY(veg_id)
			REFERENCES vegetables(id)
);

CREATE TABLE IF NOT EXISTS inseason (
	id SERIAL PRIMARY KEY,
	veg_id INTEGER,
	CONSTRAINT fk_veg
		FOREIGN KEY(veg_id)
			REFERENCES vegetables(id),
	jan TEXT,
	feb TEXT,
	mar TEXT,
	apr TEXT,
	may TEXT,
	jun TEXT,
	jul TEXT,
	aug TEXT,
	sep TEXT,
	oct TEXT,
	nov TEXT,
	dec TEXT
);
