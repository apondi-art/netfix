# Netfix

This Django-based project is a web platform designed to connect **Customers** with **Companies** that offer various home-related services.



## About

This platform allows two types of users:

- **Customers**: Can register, view services, and request them.
- **Companies**: Can register, create and manage services in their field of work.

Each user has a profile page, and services are categorized, displayed by popularity or creation date.


## Features

### User Roles

- **Customers**:
  - Register with email, password, username, and date of birth.
  - View and request services.
  - See request history.

- **Companies**:
  - Register with email, password, username, and field of work.
  - Create and manage services in their field.
  - View all services they offer.

### Services

Each service has:
- Name
- Description
- Field (e.g., Carpentry, Painting, Plumbing)
- Price per hour
- Creation date
- Associated company


## Technologies

- **Python 3**
- **Django 3.1.14**
- HTML5 / CSS3
- Django Templates

##  Installation

 **Clone the repository**
   ```bash
   git clone https://learn.zone01kisumu.ke/git/wyonyango/netfix
   cd netfix
   ```
To run the program:

**Create a virtual environment:**

```
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**Install django 3.1.14:**
```
pip install Django==3.1.14
```

**Apply migrations**
```
python3 manage.py makemigrations
python3 manage.py migrate
```
Run the server:
```
python3 manage.py runserver
```

## Contributing

Feel something’s missing or broken?

- Open an issue

- Submit a pull request with improvements

## License

This project is licensed under the [MIT License](LICENSE). 

## Contributors

[Quinter Ochieng](https://github.com/apondi-art)

[Wycliffe Onyango](https://github.com/WycliffeAlphus)