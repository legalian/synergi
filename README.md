#synergi
<h1>IN-PROGRESS</h1>
-- Pushing to github
	(with the push button and commit message dialogue)
	(pushes won't be able to be performed all the time- if someone pushes a change while they have the repo open in synergy, it's going to reject our push.)
	(if the commit+push cannot be performed, report the message back to the user so they can choose to either pull or make a new branch to resolve it.)
-- fix css syntax error on todolist.html when creating project. 


<!-- https://developer.github.com/v3/git/commits/#create-a-commit -->
<!-- https://developer.github.com/v3/git/refs/#update-a-reference -->

<h1>TODO</h1>

-- more supported datatypes (for live editing in non-raw-text form):
	JSON (completed)
	CSV  (completed)
	GSON (not completed, seems possible)
	XML  (might be possible under current system, seems easy if not)
	GEXF/GDF/GML/most of the formats supported by gephi. Most of them seem like they already work with the JSON synchronization library
	newick format

-- display images as images when opened. (not html... that would open a cross site scripting vulnerability)

<h2>Front end</h2>
	-- beautify dropdown menus in browse
	-- add a versioning system on client side that mimics the server side- that way when the server rejects a change out of step with the client, they can come to a compromise or reload when the server and client can't find common ground.
	-- make the client show some kind of message or attempt a reconnect when it gets a network error (if you close your laptop and come back you have to refresh to make things work again... this would be a source of confusion for users.)
	-- improve client side code so everything works even if the server takes obnoxiously long to respond
	-- make it so that when a pane is created or deleted it doesnt fuck up the sizes of all the other panes.


<h2>Back end</h2>
	-- update other database list to be an Array
	 not be in the session if the earlier connection you had expires
	-- need a better way to determine when someone really disconnects
		(currently, visiting and then refreshing the page sends two joins and then one disconnect.)
		(the first join adds you to the list of accessors, the second join does nothing, and the first diconnect removes them from the list of connected users even though theyre still connected and currently editing)
	-- Allowing the user to make changes to the file structure
		(there's some magic behind the scenes with github api that i'm not totally sure about. A file move is a github operation that is different from deleting-and-creating a file.)
		(deleting and (possibly)creating files could also be a goal here but idk)
	-- Create a new branch
		(button with pop-up settings. This should change the branch column in every relevant place in our database.)
	-- Automatically pushing to github and removing the session when there are no connected users
		(in the disconnect flask route, query for all sessions where connected users == "".)
		(if the push fails, because you have nobody to notify, just create a new branch with an automatically generated name to cram the users's changes. This should also change the branch column in the relevant database entries.)
		(there is a technical possibility that a user might hit the /join route but not the socket.join route, which would create a session where nobody ever connects in the first place. If you only clean up sessions when the last user disconnects, these will persist in our database indefinitely. Best way to clean these up is to query *all* ghost-town sessions when anyone disconnects.)




<h2>Updates to Synergi 2.0</h2>
	-- All pages:
		- you should be able to open an editor even if youre not logged in- you just can't save
		- logged in with github should also show your github icon
		- also log on with and keep track of aws credentials.
		- need to associate things with github account UUIDS, not account names
			- because what if they have something associated with their account and then change their github username
	-- Editor page:
		- uncollapsable ribbon on left containing different pages of settings
			- files
				- be able to see and edit project description
				- add ability to delete and rename files (on each unit) (only appears on mouseover)
				- new file, new folder (at top) (only appears on mouseover)
			- github
				-this pane just displays a "conenct to github" button if they aren't logged into github
				-this pane displays a "create repo" button if they are logged into github but don't have a repo created for the project yet
				- be able to see github repo, branch, owner
				- button to fork into new branch
				- redundant button to make a commit+push
					- modal should pop up and allow them to edit their commit.
					- the modal should also show a overview of their commit diff. (monaco has a nice diff viewer)
				- button to make a pull
			- search
				-just search
			- deploy/nodes (for graph editor)
				-this pane just displays a "conenct to github" button if they aren't logged into github
				-this pane displays a "create repo" button if they are logged into github but don't have a repo created for the project yet
				-this pane displays a "connect to AWS" button if they completed the previous two steps but aren't connected to AWS
				-this pane displays a "create hook graph file" if they've completed the previous three steps but no hooks.graph exists.
				-okay if theyve done all that then it displays a toolbox full of commonly used webhooks and a search bar to search a more complete list of normal APIs.
				- with node selected:
					-if the node is a AWS LAMBDA node:
						-you may add dependancies:
							-NPM, for js
							-pip, for py (select version of python)
						-other AWS lambda properties
					-if the node is }{<}:{>}>:{>}{>}[:}{>:
						-you may ":><":>":>":<":>":
							-)@#*$^>}@{$:|}
							-+!_)#@$(*)!&~~)@#*(
							-$$$%%%
		- collapseable pane just to the right of the ribbon containing the set of properties indicated by the settings
		- up to 3 editor panes, any more is just weird.
			- switch to monaco editor
			- buttons at tab level:
				- material icon for split pane
				- format document button (doable, with monaco)
		- synergi ribbon across the top should be more narrow on editor page
			- contain github login info, github owner and repo info
			- button to edit project name
			- button to save the project, which:
				- if they're not logged into github, it tells them to login. (and then prompts them to create a repo)
				- if they're logged into github but they don't have a repo created, it prompts the user to create a repo for it.
				- otherwise, it's the same as the commit button on the github page.





<h2>Stretch Goals</h2>
	**-- 3rd party editors
	-- add tools to editor page
	-- remove favicons 500 error
	-- change the active tabe colors in editor page
	-- Doing a manual pull
		(button with pop-up settings. Not sure how this would work behind the scenes.)
	-- change filename from todolist to browse
	-- invite system maybe





