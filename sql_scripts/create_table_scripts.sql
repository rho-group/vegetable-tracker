DROP TABLE IF EXISTS eaten;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS vegetables;

CREATE TABLE IF NOT EXISTS users (
	id SERIAL PRIMARY KEY,
	username TEXT,
	password TEXT
);

CREATE TABLE IF NOT EXISTS vegetables (
	id SERIAL PRIMARY KEY,
	foodid TEXT,
	foodname TEXT,
	foodtype TEXT,
	process TEXT,
	edport TEXT,
	igclass TEXT, 
	igclassp TEXT,
	ca TEXT,
	carotens TEXT,
	fe TEXT,
	fibc TEXT,
	fol TEXT,
	jodi TEXT,
	k TEXT,
	mg TEXT,
	nacl TEXT,
	natrium TEXT,
	nia TEXT,
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
	zn TEXT
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
