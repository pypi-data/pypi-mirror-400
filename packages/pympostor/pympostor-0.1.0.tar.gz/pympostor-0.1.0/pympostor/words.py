"""Categorías y palabras para el juego de impostor."""

import random
from typing import Dict, List, Tuple

CATEGORIES_AND_WORDS: Dict[str, List[str]] = {
    "Frutas": [
        "Manzana", "Plátano", "Naranja", "Uva", "Fresa", "Mango", "Piña", "Sandía",
        "Melón", "Pera", "Cereza", "Kiwi", "Limón", "Coco"
    ],
    "Animales": [
        "León", "Tigre", "Elefante", "Oso", "Lobo", "Zorro", "Jirafa", "Rinoceronte",
        "Hipopótamo", "Cocodrilo", "Serpiente", "Panda", "Koala", "Canguro", "Gorila",
        "Chimpancé", "Mono", "Jaguar", "Leopardo", "Puma", "Guepardo", "Cebra",
        "Caballo", "Vaca", "Cerdo", "Oveja", "Perro", "Gato", "Conejo",
        "Águila", "Pingüino", "Pavo Real", "Flamenco", "Búho",
        "Tiburón", "Ballena", "Delfín", "Pulpo", "Tortuga Marina", "Orca"
    ],
    "Países": [
        "Argentina", "México", "España", "Francia", "Italia", "Japón", "Brasil",
        "Chile", "Colombia", "Perú", "Venezuela", "Ecuador", "Uruguay", "Paraguay",
        "Estados Unidos", "Canadá", "Reino Unido", "Alemania", "Portugal", "Grecia",
        "Turquía", "India", "China", "Corea", "Tailandia", "Australia", "Nueva Zelanda",
        "Sudáfrica", "Egipto", "Marruecos", "Noruega", "Suecia", "Finlandia", "Dinamarca",
        "Islandia", "Irlanda", "Polonia", "Rusia", "Ucrania", "Croacia", "Serbia",
        "Suiza", "Austria", "Bélgica", "Holanda", "Países Bajos", "Luxemburgo",
        "Mónaco", "Andorra", "San Marino", "Vaticano", "Malta", "Chipre", "Islandia",
        "Groenlandia", "Cuba", "República Dominicana", "Puerto Rico", "Jamaica",
        "Barbados", "Trinidad y Tobago", "Panamá", "Costa Rica", "Nicaragua", "Honduras",
        "Guatemala", "Belice", "El Salvador", "Bolivia", "Guyana", "Surinam"
    ],
    "Videojuegos": [
        "Mario", "Zelda", "Pokémon", "Fortnite", "Minecraft", "Call of Duty",
        "FIFA", "Grand Theft Auto", "Assassin's Creed", "The Witcher", "Skyrim",
        "Fallout", "Red Dead Redemption", "God of War", "Uncharted", "Horizon",
        "Spider-Man", "Batman", "Superman", "Street Fighter", "Tekken", "Mortal Kombat",
        "Counter-Strike", "Valorant", "League of Legends", "Dota", "Overwatch",
        "Apex Legends", "Rocket League", "Among Us", "Animal Crossing", "Splatoon",
        "Final Fantasy", "Kingdom Hearts", "Persona", "Dark Souls", "Bloodborne",
        "Elden Ring", "Sekiro", "Resident Evil", "Silent Hill", "Dead Space",
        "The Last of Us", "Uncharted", "Tomb Raider", "Doom", "Quake", "Half-Life",
        "Portal", "Bioshock", "Mass Effect", "Dragon Age", "Halo", "Gears of War",
        "GTA", "Watch Dogs", "Far Cry", "Just Cause", "Mafia", "Yakuza",
        "Persona", "Fire Emblem", "Xenoblade", "Monster Hunter", "Dark Souls",
        "Elden Ring", "Sekiro", "Nioh", "Ghost of Tsushima", "Death Stranding"
    ],
    "Películas": [
        "Titanic", "Avatar", "Avengers", "Star Wars", "Harry Potter", "El Señor de los Anillos",
        "Matrix", "Jurassic Park", "Terminator", "Alien", "Predator", "RoboCop",
        "Blade Runner", "Inception", "Interstellar", "Gladiator", "Braveheart",
        "Forrest Gump", "Pulp Fiction", "The Godfather", "Scarface", "Goodfellas",
        "Casablanca", "Citizen Kane", "Psycho", "The Shining", "The Exorcist",
        "Jaws", "E.T.", "Back to the Future", "Indiana Jones", "James Bond",
        "Iron Man", "Captain America", "Thor", "Hulk", "Black Widow", "Spider-Man",
        "Batman", "Superman", "Wonder Woman", "Aquaman", "Flash", "Green Lantern",
        "Deadpool", "Wolverine", "X-Men", "Guardians of the Galaxy", "Doctor Strange",
        "Black Panther", "Ant-Man", "Captain Marvel", "Shazam", "Venom",
        "Fast and Furious", "Mission Impossible", "John Wick", "Taken", "Die Hard",
        "The Dark Knight", "Joker", "The Joker", "Suicide Squad", "Justice League",
        "Transformers", "Pacific Rim", "Godzilla", "King Kong", "Cloverfield",
        "The Conjuring", "Insidious", "Annabelle", "The Nun", "It", "The Shining",
        "Get Out", "Us", "A Quiet Place", "Bird Box", "The Purge", "Saw", "Halloween"
    ],
    "Celebridades": [
        "Leonardo DiCaprio", "Brad Pitt", "Tom Cruise", "Will Smith", "Johnny Depp",
        "Robert Downey Jr", "Chris Evans", "Chris Hemsworth", "Tom Hanks", "Denzel Washington",
        "Morgan Freeman", "Samuel L. Jackson", "Harrison Ford", "Matt Damon", "Ben Affleck",
        "Ryan Reynolds", "Hugh Jackman", "Ryan Gosling", "Jake Gyllenhaal", "Christian Bale",
        "Scarlett Johansson", "Jennifer Lawrence", "Emma Stone", "Natalie Portman", "Anne Hathaway",
        "Meryl Streep", "Julia Roberts", "Sandra Bullock", "Nicole Kidman", "Cate Blanchett",
        "Angelina Jolie", "Jennifer Aniston", "Cameron Diaz", "Reese Witherspoon", "Emma Watson",
        "Margot Robbie", "Gal Gadot", "Zendaya", "Florence Pugh", "Anya Taylor-Joy",
        "Taylor Swift", "Beyoncé", "Ariana Grande", "Lady Gaga", "Rihanna",
        "Katy Perry", "Adele", "Billie Eilish", "Dua Lipa", "Olivia Rodrigo",
        "The Weeknd", "Drake", "Post Malone", "Ed Sheeran", "Bruno Mars",
        "Justin Bieber", "Shawn Mendes", "Harry Styles", "Bad Bunny", "J Balvin",
        "Cristiano Ronaldo", "Lionel Messi", "Neymar", "Kylian Mbappé", "LeBron James",
        "Michael Jordan", "Kobe Bryant", "Serena Williams", "Roger Federer", "Rafael Nadal",
        "Tiger Woods", "Usain Bolt", "Tom Brady", "Conor McGregor", "Floyd Mayweather",
        "Elon Musk", "Jeff Bezos", "Bill Gates", "Mark Zuckerberg", "Warren Buffett",
        "Oprah Winfrey", "Ellen DeGeneres", "Jimmy Fallon", "Stephen Colbert", "Conan O'Brien"
    ],
    "Comidas": [
        "Pizza", "Hamburguesa", "Tacos", "Sushi", "Pasta", "Pollo", "Carne", "Pescado",
        "Arroz", "Pan", "Queso", "Huevo"
    ],
    "Deportes": [
        "Fútbol", "Básquetbol", "Tenis", "Natación", "Boxeo", "Voleibol", "Béisbol",
        "Golf", "Fútbol Americano", "Fórmula 1"
    ],
    "Lugares": [
        "Torre Eiffel", "Estatua de la Libertad", "Big Ben", "Coliseo", "Machu Picchu",
        "Gran Muralla China", "Taj Mahal", "Pirámides de Egipto", "Disneyland"
    ],
    "Ropa": [
        "Camisa", "Pantalón", "Vestido", "Zapatos", "Jeans", "Gorra", "Reloj", "Mochila"
    ],
    "Naturaleza": [
        "Árbol", "Flor", "Montaña", "Sol", "Luna", "Estrella", "Nube", "Lluvia", "Arcoíris"
    ],
    "Series de TV": [
        "Breaking Bad", "Game of Thrones", "The Walking Dead", "Stranger Things",
        "Friends", "The Office", "The Big Bang Theory", "How I Met Your Mother",
        "Lost", "Prison Break", "24", "House of Cards", "Orange is the New Black",
        "Narcos", "Money Heist", "La Casa de Papel", "Élite", "Dark", "Squid Game",
        "The Crown", "The Mandalorian", "WandaVision", "Loki", "The Falcon and the Winter Soldier",
        "Cobra Kai", "The Boys", "Invincible", "Rick and Morty", "South Park",
        "The Simpsons", "Family Guy", "American Dad", "Archer", "BoJack Horseman",
        "Better Call Saul", "Ozark", "The Witcher", "The Last Kingdom", "Vikings",
        "Peaky Blinders", "Sherlock", "Doctor Who", "Black Mirror", "Westworld"
    ],
    "Superhéroes": [
        "Superman", "Batman", "Spider-Man", "Iron Man", "Captain America", "Thor",
        "Hulk", "Black Widow", "Wonder Woman", "Aquaman", "Flash", "Green Lantern",
        "Wolverine", "Deadpool", "Black Panther", "Doctor Strange", "Ant-Man",
        "Captain Marvel", "Shazam", "Venom", "Daredevil", "Punisher", "Blade",
        "X-Men", "Fantastic Four", "Avengers", "Justice League", "Guardians of the Galaxy",
        "Thanos", "Loki", "Joker", "Harley Quinn", "Catwoman", "Poison Ivy",
        "Magneto", "Professor X", "Storm", "Jean Grey", "Cyclops", "Nightcrawler"
    ],
    "Marcas": [
        "McDonald's", "Burger King", "KFC", "Pizza Hut", "Domino's", "Subway", "Starbucks",
        "Nike", "Adidas", "Puma", "Under Armour", "Converse", "Vans",
        "Apple", "Samsung", "Google", "Microsoft", "Amazon", "Tesla", "Sony", "Nintendo",
        "Ferrari", "Lamborghini", "Porsche", "BMW", "Mercedes", "Audi", "Toyota", "Honda",
        "Coca-Cola", "Pepsi", "Red Bull",
        "Disney", "Netflix", "Spotify", "YouTube", "Instagram", "Facebook"
    ],
}


def get_random_category_and_word() -> Tuple[str, str]:
    """Obtiene una categoría y palabra aleatoria para el juego."""
    category = random.choice(list(CATEGORIES_AND_WORDS.keys()))
    word = random.choice(CATEGORIES_AND_WORDS[category])
    return word, category
