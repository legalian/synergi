#synergi
<h1>IN-PROGRESS</h1>
<ol>
	<li>more supported datatypes (for live editing in non-raw-text form): 
		<ol>
			<li>JSON (completed)</li>
			<li>CSV  (completed)</li>
			<li>GSON (not completed, seems possible)</li>
			<li>XML  (might be possible under current system, seems easy if not)</li>
			<li>GEXF/GDF/GML/most of the formats supported by gephi. Most of them seem like they already work with the JSON synchronization library</li>
			<li>Newick format</li>
		</ol>
	</li>
	<li>display images as images when opened. (not html... that would open a cross site scripting vulnerability)</li>
	<li>do a git pull every time the page refreshes</li>
</ol>



<h1>Front end</h1>
	<ol>
		<li>on the edit page make the file structure pane sized so you can see all of the file names, and it starts scrolled too far to the right</li>
		<li>fix cursor bug when hovering over links. <ol><li>(files in edit page, delete project button, etc.)</li></ol></li>
		<li>beautify dropdown menus in browse</li>
		<li>add a versioning system on client side that mimics the server side
			<ol><li>that way when the server rejects a change out of step with the client, they can come to a compromise or reload when the server and client can't find common ground.</li></ol>
		</li>
		<li>make the client show some kind of message or attempt a reconnect when it gets a network error <ol><li>(if you close your laptop and come back you have to refresh to make things work again... this would be a source of confusion for users.)</li></ol></li>
		<li>improve client side code so everything works even if the server takes obnoxiously long to respond</li>
		<li>rewrite project post request to be an ajax post instead of html form (todolist.html line 103)</li>
		<li>make it so that when a pane is created or deleted it doesnt fuck up the sizes of all the other panes.</li>
	</ol>



<h1>Back end</h1>
	<ol>
		<li>update other database list to be an Array</li>
		<li>not be in the session if the earlier connection you had expires</li>
		<li>need a better way to determine when someone really disconnects
			<ol>
				<li>currently, visiting and then refreshing the page sends two joins and then one disconnect.</li>
				<li>the first join adds you to the list of accessors, the second join does nothing, and the first diconnect removes them from the list of connected users even though theyre still connected and currently editing</li>
			</ol>
		</li>
		<li>Allowing the user to make changes to the file structure
			<ol>
				<li>there's some magic behind the scenes with github api that i'm not totally sure about. A file move is a github operation that is different from deleting-and-creating a file.</li>
				<li>deleting and (possibly)creating files could also be a goal here but idk</li>
			</ol>
		</li>
		<li>Create a new branch
			<ol><li>button with pop-up settings. This should change the branch column in every relevant place in our database.</li></ol>
		</li>
		<li>Automatically pushing to github and removing the session when there are no connected users
			<ol>
				<li>in the disconnect flask route, query for all sessions where connected users == "".</li>
				<li>if the push fails, because you have nobody to notify, just create a new branch with an automatically generated name to cram the users's changes. This should also change the branch column in the relevant database entries.</li>
				<li>there is a technical possibility that a user might hit the /join route but not the socket.join route, which would create a session where nobody ever connects in the first place. If you only clean up sessions when the last user disconnects, these will persist in our database indefinitely. Best way to clean these up is to query *all* ghost-town sessions when anyone disconnects.</li>
			</ol>
		</li>
	</ol>

<h2>Stretch Goals</h2>
	<ol>
		<li>3rd party editors</li>
		<li>add tools to editor page</li>
		<li>remove favicons 500 error</li>
		<li>Doing a manual pull(button with pop-up settings.)</li>
		<li>change filename from todolist to browse</li>
		<li>invite system maybe</li>
	</ol>

<h1>Known bugs</h1>
	<ol>
		<li>putting underlined characters in a file prevents editing</li>
	</ol>