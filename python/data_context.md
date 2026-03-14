# Data Context — Field Definitions

This file provides the AI agent with additional context about your dataset.
Fill in each section for the fields in your data. The agent will use this
to give more accurate, meaningful answers.

---

## Field Descriptions

Explain what each column means in plain language.

| Field Name | Description |
|---|---|
| `franchID` | `The Major League Baseball team identifier spelled out in three letters.` |
| `divID` | `The MLB division each team played in during that year which may change over time. North, South, East, and West. The divisions are unique to the leagues (lgID).` |
| `R` | `Runs or how many runs were scored in that season by each team. This is how many times a player crossed home plate to score a run or point for their team.` |
| `AB` | `At bats, or the number of times a player stood at Home Plate in the offensive side of the inning hitting for their team trying to score a run.` |
| `HR` | `Home Runs. How many times a player hit the ball over the outfield fence in the field of play resulting in at least one run scored. If other players were on base when the home run was hit then they also score runs or points for the offensive team.` |
| `SB` | `Stolen Bases. During the offensive side of the inning how many times did a player advance to the next base without the hitter putting the ball in play.` |

---

## Value Mappings

Define what coded or abbreviated values mean.

| Field Name | Value | Meaning |
|---|---|---|
| `DivWin` | `Y` | Yes |
| `DivWin` | `N` | No |
| `LgWin` | `Y` | Yes |
| `LgWin` | `N` | No |
| `WSWin` | `Y` | Yes |
| `WSWin` | `N` | No |
| `priority` | `Y` | Yes |
| `priority` | `N` | No |

---

## Units & Format

Specify the units or format of numeric and date fields so the agent interprets them correctly.

| Field Name | Unit / Format | Notes |
|---|---|---|
| `attendance` | Integer (people) | Total Attendance for the season |

---

## Business Rules

Define thresholds, targets, or logic the agent should know about when interpreting the data.

- **WSWin**: To win the World Series the team must also have won their League (LgWin) and Division (DivWin)

---

## General Notes

Add any other context the agent should know about this dataset.

- This data is refreshed manually
- Exclude any rows where `franchID` is blank — these are test records
- The dataset covers multiple years (2010 - 2021)