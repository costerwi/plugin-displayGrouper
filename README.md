# plugin-displayGrouper
This is a collection of Abaqus/CAE plugins to help work with the currently displayed elements (display group) in the Visualizer module.
Display group manipulations are performed in a compatible way such that the "Undo" and "Redo" buttons in the "Create Display Group" dialog will operate as expected.

### Display Grouper plugins
The following functions are included.

- **Add adjacent elements** - Search for elements which share nodes with the currently active elements. These elements will be added to the display group.
- **Add attached elements** - Search for elements which share nodes with the currently active elements directly or indirectly through other elements. These elements will be added to the display group.
- **Add nearby elements...** - Add elements with undeformed nodes close to the currently active undeformed nodes. The plugin will prompt the user for a search radius. This works best with a small number of active elements and a relatively small search radius.
- **Add same section assignment elements** - Add elements with the same section assignment as active elements.
- **Create named from section assignments** - Create a named display group for each element section definition. This may be useful to assign different plot states in the Display Group Manager.
- **List section assignments of active elements**
- **Remove elements with picked section assignment** - Allow user to click on an element, remove all elements with the same section assignment, and then prompt user to click another element. Repeat until cancelled. Useful to peel back the onion of an assembly.
- **Remove picked elements** - Remove elements selected in viewport and then prompt for more elements to remove. Repeat until cancelled.

## Installation instructions

1. Download and unzip the [latest version](https://github.com/costerwi/plugin-displayGrouper/releases/latest)
2. Double-click the included `install.cmd` or manually copy files into your abaqus_plugins directory
3. Restart Abaqus CAE and you will find the above scripts in the Assembly module plug-ins menu

![image](https://github.com/costerwi/plugin-displayGrouper/assets/7069475/2f4fa9d7-4d32-426d-8ea0-f5df42e136e4)
