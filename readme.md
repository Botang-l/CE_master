# ORA Project : The optimal scheduling problem for train captains at the Taiwan Railways Administration.
###### tags: `ORA`、`Project`

> This project is the final project for the Operations Research Applications and Implementation Course at National Cheng Kung University.

This project focuses on the optimization of scheduling for train captains at the Taiwan Railways Administration.


- File in this project
```
─ORA_term_project/
    └─code/
    |   ├─term_project.py
    |   ├─draw_result.ipynb
    |   ├─TRA.csv 
    └─doc/    
    |   ├─presentation.pptx
    |   ├─Mathematical_models.pdf
    └─result/
        ├─工作班_0.png 
           :
           :
        ├─工作班_58.png 
```
- term_project.py
    > the code is used to this term project
- draw_result.ipynb
    > the code is used to generate the pictures from the result in our mathematical model.
- TRA.csv
    > the data of Taiwan Railways Administration
- presentation.pptx
    > the powerpoint is used to our final presentaton
- Mathematical_models.pdf
    > the explaination of mathematical model in our project, including decision variable, objective Fuction, and constraints. 
## Problem Definition

### Noun Definition
1. Crew schedule: A crew schedule is the work schedule for a train captain for a given day.
2. Duty: Duty refers to train service x, which departs from location A at a specific time and arrives at location B at a specific time.
3. Rest period: The time interval between two duties, during which the train captain must remain at the station but is not counted as working hours."

### Problem Description

Scheduling for train captains is currently done manually based on experience, and creating an optimal schedule is a highly complex problem. The reasons for this are as follows:

>- Train departure times are fixed and cannot be changed, so employees must work within these time constraints.
>- Scheduling must take into account spatial factors, meaning that the starting and ending locations for a crew schedule should be the same, and that employees should return to their starting location at the end of a crew schedule that spans multiple days.
>- Overtime pay is required for crew schedules that exceed 400 minutes, but train captains are paid a monthly salary. As a result, the company would prefer for crew schedules to be close to but not exceed 400 minutes.

The following factors contribute to poor work quality as a result of scheduling:

> - **Rest periods that are too short or too long**
>*If rest periods are too short, train captains do not have enough time to rest.
If rest periods are too long, the company is unable to effectively use its workforce, requiring more employees to cover train service.*
For train captains, long rest periods are also unproductive and unpaid.
> - **Significant variation in the length of crew schedules**
*There may be crew schedules that last 12 hours and others that last only 2 hours.*
>- **Total working hours that are too short or too long**

### Solution Proposal

- There should not be too much time between duties within a crew schedule
- There should not be too much variation in the length of crew schedules.
- The total length of a crew schedule should not be too long or too short.
- There should be appropriate rest periods between duties.


## Mathematical models
- Rest periods are counted as working hours.
- Overtime pay is available for crew schedules that exceed 400 minutes.

### Decision Valuable

- $x^{t}_{d,i}$: A binary decision variable that indicates whether train service t is the i-th train service of crew schedule d.
Where $𝑡∈𝑇，𝑑∈D，𝑖∈𝐼$.



### Constraint

- $\sum_{𝑡∈𝑇}{x^{t}{d,i}\le 1}$: Ensures that each duty is assigned to only one train service.

-  $\sum_{𝑡∈𝑇}{x^{t}{d,i}}$ $\ge$ $\sum_{𝑡∈𝑇}{x^{t}_{d,i+1}}$: Ensures that the n+1 duty is only selected if the n duty is selected.

- Spatial and Time constraint
we will discuss two cases time and spatial constraint formulas

Case 1: Considering the continuity of train services

![](https://playlab.computing.ncku.edu.tw:3001/uploads/upload_74579f0c9e211ae77a10719766b9cee6.png)x

Case 2: Considering the end of a duty

![](https://playlab.computing.ncku.edu.tw:3001/uploads/upload_d7d76b72e6318e66ac127c6248298b11.png)

#### Spatial constraint: 

![image](https://user-images.githubusercontent.com/83536674/211263677-401e68ff-7b88-4d8c-af71-b1db4305b5de.png)



Where $ES_t$ is the arrival station of train service t, and $SS_t$ is the departure station of train service t.

The following is an analysis of the spatial constraint formula:

Case 1: For duty 1, the right side of the equation is zero, so the arrival location of duty 1 must be the same as the starting location of duty 2.
Case 2: For duty 2, the right side of the equation is not zero, so there is no constraint between duties 2 and 3.

#### Time constraint: 

![image](https://user-images.githubusercontent.com/83536674/211263820-78564915-de01-4600-a6e7-743e3e6eba9b.png)

Where ET and ST are the departure and arrival times of the train service, and SP is the time for boarding and disembarking.

The following is an analysis of the time constraint formula:

Case 1: For duty 1, the right side of the equation is zero, so the arrival time of duty 1 plus the boarding and disembarking time should be less than or equal to the starting time of duty 2.
Case 2: For duty 2, the right side of the equation is not zero, so there is no constraint between duties 2 and 3.





### Objective Fuction

**The objective function is minimized by: (overtime pay * overtime hours) + (base salary * number of Crew schedules)**.
- If the work exceeds 400 minutes, the overtime hours in the objective function will increase. 
- If an employee works for a shorter time, it is still equivalent to working for 400 minutes, and a shorter work time usually means more manpower is needed to complete the schedule, so the value of the objective function is likely to increase. The above two points tend to give each employee almost 400 minutes of work time.


## Contributing 

- The number of crew schedules has decreased from 73 to 59.
- Resulting in a 25% decrease in labor costs.

## Future Work

- The actual schedule can be split, but the schedule being solved for cannot be split.

- More human-centered design, such as the rest time between two crew schedules, can be considered.


## Release History

* 0.1.0
    * Work in progress



