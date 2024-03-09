# RPi Pico W Bike Computer: Revision 1

## Overview
The inspiration for this project came about from my desire to combine my recent hobbies of 3D modeling, 3D printing, Electronics and IoT programming, all hobbies that I have picked up in the past year. 

I was introduced to the Raspberry Pi Pico boards in February of 2023 and have been building up smaller miscellaneous projects to gain familiarity with both the Pico board specifically, as well as general electronics fundamentals. After completing an RFID Spotify Record Player and a simple handheld device with the Pico, I felt I was ready enough to take on a project that adequately encapsulated and showcased the skills and progress made over the past year with these hobbies. When the idea first hit me to start building out a bike computer, I started doing some exploration into how feasible this project would be with the Pico and if I could even connect to the power meter that came installed on my Canyon Endurace (a 4iiii Precision+ (?) meter). Before this project, I had not worked with Bluetooth as a technology, so step one was to begin familiarizing myself with the BTLE Specifications and how the communication protocol worked. After first watching a video on BTLE for the Raspberry Pi Pico W (probably the only such video that existed on the topic) I wrote two simple programs (one for an Advertiser device and one for a Client device, both to be run on separate Picos) to send simple commmands from the Advertiser to the Client via BTLE connection. (Sidenote, the application for sending commands (the Advertiser) was the first ~useful~ application loaded onto the handheld device I made previously). Once this was working successfully, I was able to modify the Client code to connect to the 4iiii Precision Meter and receive *some kind* of data (I didn't quite know the parsing of the data or how to interpret the Service flags at this point, but I was getting data and this seemed like a promising enough development to begin laying out how this project could proceed).

Now came the fun part which was designing the device and clearly defining the capabilities and features I would want/could realistically implement in a bike computer. I laid out my Bill of Materials and came up with the following:

1) Raspberry Pi Pico W - $6
2) 3.7v Rechargeable LiPo battery - $9
3) MicoSD Card Module - $4
4) 1.28" SPI TFT Screen (based on the GC9A01 driver) - $6
5) Power Switch - $0.40
6) Tactile Buttons x3 - $0.10/button

With my BOM assembled and the components acquired, I set about visualizing what these components would look like in a 3D space to figure out the most compact and effective layout that could be achieved given the setup. This part of the process involved simply stacking the components in a layout in which all components would be able to interface with eachother as needed while being ergonomic and intuitive. After getting a rough idea of the layout, it was time to start iterating on prototypes in Fusion360. Measurements were taken using digital calipers and the sketching began. For this particular project, I began by creating the "front" of the case which would hold the screen and also contain the screen and button cutouts. The general modeling workflow for this looked like: 

1) Build out the current model body until I hit a "milestone" for features that I wanted to test a fit for
2) Printing out the body and testing the fit before either:
    - a) making tweaks to the fit and printing out another iteration or
    - b) moving on to the next set of features/milestone
    
> It should be noted that all prototype prints were completed using a Bambu Lab P1S printer using a .4mm nozzle and Bambu classic PLA. 

Modeling out this bike computer was undoubtedly the first project that I approached with a real emphasis on thoughtful design. The final design for this ended up consisting of 5 separate parts that snapped together to provide the necessary support and clearance between all parts in the enclosure. An overview of the parts and their functions is as follows:

1) **Case Top** - Contains cutouts and mounting pegs for the screen, a cutout for the Pico's microUSB port, cutouts for the buttons, a power switch cutout, male snap fit pieces which snap into the bottom of the case, and two levels of female snap points in which both dividers snap into.
2) **Upper Divider** - Snaps into the Case Top and contains an ident and mounting posts for the Pico board on one side as well as a shelf for holding the button pad on the opposite side.
3) **Bottom Divider** - Snaps into the Case Top and contains an indent and mounting posts for the microSD card module as well as a divider for the battery.
4) **Case Bottom** - Contains the female snap fit points for the Case Top to snap into as well as a cutout for accessing the microSD card.


Upon settling on a completed prototype, I printed out the final product using Bambu Lab PETG-CF (Carbon Fiber) filament and began the component assembly. Assembly consisted of precisely measuring the proper length of each wire to its respective pin on the Pico and soldering the connections (I was still using cheap DuPont wires with the ends cut off when doing this the first time, but I've grown out of those now). The final pinout came out like so:



| **Buttons**             | **GPIO** |
| --------                | -------- |
| Left                    | 22       |
| Center                  | 21       |
| Right                   | 20       |

<br/>

| **Display**             | **GPIO** |
| --------                | -------- |
| CS                      | 13       |
| RESET                   | 18       |
| DC                      | 12       |
| SCK                     | 10       |
| MOSI                    | 11       |

<br/>

| **MicroSD Card Module** | **GPIO** |
| --------                | -------- |
| SCK                     | 2        |
| MOSI                    | 3        |
| MISO                    | 4        |
| CS                      | 1        |

<br/>
___
<br/>
<br/>
After finishing the assembly I crossed my fingers and flipped the power switch. Incredibly, it powered on. With the device up and running I went for my first test ride. I had fleshed out the program only to the point of displaying the power data, but it seemed to be transmitting accurately and reliably. After this I set about fleshing out the bulk of the program. This consisted of building out a way of navigating menus and setting up a multi-threaded approach for handling all of the services that would need to be running concurrently, which brings me to the current state of the project. 

The program currently attempts to find a connection on boot, with an option to skip pairing by holding down the right button. After either skipping the connection or successfully pairing, the user lands on the main menu of the application. From there, a user has the option to pair with a meter, view ride history saved to the microSD card, or start a ride. (Stretch goal here is to also have a workout option which would allow users to follow a Zwift styled workout). From the main menu, there is also a status indicator for the status of a Bluetooth connection. When starting a simple ride, the screen displays the current power, current cadence, and elapsed time. On every screen update (roughly every second, when data is received from the meter) the data is appended to an in-memory map/dictionary and a separate asynchronous task writes this data to a unique ride file on the microSD card every minute and clears the in-memory value to prevent memory depletion. The user can pause a ride, and from the pause screen, can either continue or exit the ride, upon which a summary of the ride is shown showcasing the average power, average cadence, and total ride time. The software development of this application is an ongoing process, but the pre-defined MVP requirements have been met.

## Project Obstacles:
 - Working with the GC9A01 driver... There were no good micropython libraries for this driver and in order to get the performance I would need for this application I ended up finding the (Link to Hughes repo written in C++) repo and having to build custom firmware to include this custom module. This was my first time compiling firmware and this task seemed more daunting than it was in reality, but it did end up consuming quite a bit of time and came with a good amount of trial and error. Notably, after finally getting a working build with the custom driver module included, the micropython version being used by the repo was several versions behind the current release and did not have bluetooth library support baked in, so I was forced to rebuild with a more recent micropython release.

 - Interpretting the transmitted power meter data required a decent amount of poring over the Bluetooth Cycling Power Specification to understand how to read the service flags and isolate the data that I wanted. 

 - Building out a "contextual" navigation system to handle asynchronous service and task handling required a bit of thought, but the solution is one that is highly extendable and rather performant to the limitations of the board. This contextual navigation system handles display updates, button command handling, and background tasks concurrently.

 - Handling the ride data in memory in a way that doesn't exceed the flash mem of the Pico while not slugging performance of other threaded functions and causing noticeable performance hits from the ride experience.

Future Targets:
 - As mentioned above, the functionality for doing a workout would be a highly desirable feature. This would entail coming up with a new "workout context" in which a list of all of the phases in a workout could be stored and traversed while simultaneously providing feedback for the actual current power/cadence versus the target goal/cadence in the workout phase. Something like:

```
 workout = [
    {
        "time": 5:00, # The duration of this phase
        "target_power": 185 # The power that should be maintained for this phase
        "target_cadence": 90 # The pedal stroke RPM for this phase
    },
    {
        "time": 1:30, # The duration of this phase
        "target_power": 275 # The power that should be maintained for this phase
        "target_cadence": 100 # The pedal stroke RPM for this phase
    }
 ]
 ```

 - Additionally, there should be an option for uploading ride data to a cloud database over WiFi, and a simple online dashboard to show the full history of the ride as well as full analytics and total cycling progression. 