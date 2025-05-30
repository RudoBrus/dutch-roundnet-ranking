# Dutch Roundnet Ranking

This repository contains the code to calculate the Dutch roundnet ranking. The
ranking system is inspired by the Swiss ranking system, which is explained in
detail in [this video](https://www.swissroundnet.ch/post/power-ranking-system).
Additionally, our reasoning for adopting this system is documented
[here](https://docs.google.com/document/d/1JMMrFDL7OXA6E0sV2qaR03Z_aBW44RY8GLCWnPag4YA/edit?tab=t.0).

## Quick summary of the ranking system

The ranking system allows players to earn points by participating in
tournaments. A player's ranking is determined by summing up their three best
tournament results. The points earned in a tournament depend on the player's
placement and the strength of the competition. Over time, older tournaments
contribute fewer points to the ranking.

## The rankings

The rankings are made per category (`women`, `advanced`, `intermediate` and
`beginner`). They are saved as CSV in the [rankings](./rankings) directory. We
also save the tournament history in which you can see the relevant tournaments
and which multipliers they currently have.

## Updating the ranking

### Getting the tournament data

In order to be able to update the ranking, first of all you will need to have
the tournament data. This can be gathered using the
[Fwango scraper](./fwango_scraper).

### Running the ranking calculator

You can update the ranking calculator by opening a pull request and tagging it
with "update-ranking". Once the pull request is created, GitHub automation will
generate a commit that updates the ranking. After reviewing the changes, you can
merge the pull request.

Alternatively, you can run the ranking calculator locally by executing the
following command:

```bash
pipenv run python -m ranking_calculator
```

You can optionally specify categories using the --categories flag. For example:

```bash
pipenv run python -m ranking_calculator --categories advanced women
```

## Experimenting

If you feel like the current tuning of the ranking system could be better, feel
free to experiment by tuning the parameters in the
[config](./ranking_calculator/config.py). All the parameters used are in this
document, including explanation on what they do. You can change them and then
run the ranking calculator to see the effects. If you have anything else you
would like to see change, feel free to open up an issue
[here](https://github.com/RudoBrus/dutch-roundnet-ranking/issues), or even
better, create a pull request that implements the change!

## Setting up for developers

To contribute to this project, follow these steps to set up your development
environment:

- **Install Python 3.10**  
   Ensure you have Python 3.10 installed on your system. You can download it from
  the [official Python website](https://www.python.org/downloads/) or use a package
  manager like `brew` on macOS:
  ```bash
  brew install python@3.10
  ```
- **Install pipenv**  
   Install `pipenv` to manage dependencies and virtual environments:
  ```bash
  pip install pipenv
  ```
- **Install project dependencies**  
   Navigate to the project directory and install the dependencies:
  ```bash
  pipenv install
  ```
- **Contribute via pull requests**  
  When making changes to the project, create a new branch for your work and
  submit a pull request. Ensure your branch is up-to-date with the main branch
  and that you have run the
  [validation script](./scripts/validation_script.bash) before submitting.
