#synergi
<h1>IN-PROGRESS</h1>


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
	--backend changes:
		owners and repos should be stored as UUIDs, instead of names.
		sessions can be spawned without hitting a projectID (editor will have to add the sessionID to the query string on client side so you can refresh without losing your progress.)
		someone who isn't logged in should be able to spawn a session, they just can't edit an existing repo.
		need to support aws login
		expand versioning system to remember all changes since last commit

<h1>Front end</h1>
	<ol>
		<li>Site beauty<ol>
			<li>beautify dropdown menus in browse</li>
			<li>make it so that when a pane is created or deleted it doesnt fuck up the sizes of all the other panes.</li>
		</ol></li>
		<li>Site robustness<ol>
			<li>add a versioning system on client side that mimics the server side<ol>
				<li>that way when the server rejects a change out of step with the client, they can come to a compromise or reload when the server and client can't find common ground.</li>
			</ol></li>
			<li>make the client show some kind of message or attempt a reconnect when it gets a network error<ol>
				<li>if you close your laptop and come back you have to refresh to make things work again... this would be a source of confusion for users.</li>
			</ol></li>
			<li>improve client side code so everything works even if the server takes obnoxiously long to respond</li>
			<li>batch changes together into one message to reduce network overhead</li>
		</ol></li>
	</ol>

<h1>Back end</h1>
	<ol>
		<li>update other database list to be an Array</li>
		<li>not be in the session if the earlier connection you had expires</li>
		<li>wait at least 60 seconds after the last person disconnects from a session to end it.
			<ol>
				<li>after ending the session, try to push to github</li>
				<li>if the push fails (branch doesnt exist or maybe they did a push from desktop while the session was open), switch your branch to synergi(n) where n is the lowest number that makes the text a new branch.</li>
			</ol>
		</li>
		<li>Allowing the user to make changes to the file structure
			<ol>
				<li>there's some magic behind the scenes with github api that i'm not totally sure about. A file move is a github operation that is different from deleting-and-creating a file.</li>
				<li>deleting and (possibly)creating files could also be a goal here but idk</li>
			</ol>
		</li>
		<li>Fork into new branch
			<ol><li>button with pop-up settings. This should change the branch column in every relevant place in our database.</li></ol>
		</li>
	</ol>

<h2>Stretch Goals</h2>
	<ol>
		<li>3rd party editors</li>
		<li>add color indicators to see who's editing what<ol>
			<li>at the file level</li>
			<li>at the individual text level</li>
		</ol></li>
		<li>add tools to editor page</li>
		<li>remove favicons 500 error</li>
		<li>Doing a manual pull(button with pop-up settings.)</li>
		<li>change filename from todolist to browse</li>
		<li>invite system maybe</li>
		<li>more supported datatypes (for live editing in non-raw form)<ol>
			<li>JSON</li>
			<li>CSV</li>
			<li>GSON</li>
			<li>XML</li>
			<li>GEXF/GDF/GML</li>
		</ol></li>
		<li>display images as images when opened</li>
	</ol>




