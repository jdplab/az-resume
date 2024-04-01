import azure.functions as func
from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.core.exceptions import AzureError
import os

def main(documents: func.DocumentList, context: func.Context) -> str:
    if documents:
        for doc in documents:
            try:
                post = doc.to_dict()
            except Exception as e:
                context.log.error(f"Error converting document to dictionary: {str(e)}")
                continue

            try:
                html = render_html_page(post)
            except Exception as e:
                context.log.error(f"Error rendering HTML page: {str(e)}")
                continue

            try:
                blob_service_client = BlobServiceClient.from_connection_string(os.getenv('STORAGE_CONNECTIONSTRING'))
                blob_client = blob_service_client.get_blob_client(os.getenv('WEB_CONTAINER'), 'posts/' + post['id'] + 'blogpost.html')
            except Exception as e:
                context.log.error(f"Error getting environment variables or creating Blob client: {str(e)}")
                continue

            try:
                cnt_settings = ContentSettings(content_type='text/html')
                blob_client.upload_blob(html, blob_type="BlockBlob", content_settings=cnt_settings, overwrite=True)
            except AzureError as e:
                context.log.error(f"Error saving HTML page in Azure Blob Storage: {str(e)}")
                continue

        context.log.info("HTML page generated and saved in Azure Blob Storage")

def render_html_page(post):
    tags = ",".join(post['tags'])
    return f"""
<!DOCTYPE HTML>
<html lang="en">
    <head>
        <title>{post['title']}</title>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no" />
        <meta http-equiv="content-type" content="text/html"/>
        <meta name="keywords" content="{tags}"/>
        <meta name="description" content="{post['title']}"/>
        <meta name="author" content="Jonathan Polansky"/>
        <link rel="icon" href="images/terminal.ico">
		<link rel="stylesheet" href="assets/css/main.css" />
		<script src="https://cdn.tiny.cloud/1/q7648hvurw1lf6ch14apkg45x4hgmmklcvkiytmydm58iqyp/tinymce/7/tinymce.min.js" referrerpolicy="origin"></script>
    </head>
    <body class="is-preload">
        <div id="navbar">
			<div class="navbar-container">
				<nav id="nav">
					<div href="#" id="iconborder" onclick="toggleMenu()">
						<div id="iconcolor">
							<a class="icon" onclick="event.stopPropagation(); toggleMenu()"><i class="fa fa-bars"></i></a>
						</div>
					</div>
					<div id="links">
						<a href="index.html">Main</a>
						<a href="blogindex.html">Blog</a>
						<a href="resume.html">Resume</a>
						<a href="index.html#contact">Contact</a>
						<a id="loginButton" class="link-class" href="javascript:void(0);" onclick="login()">Login</a>
					</div>
				</nav>
			</div>
		</div>

        <header id="header">
            <div class="inner">
                <a href="https://linkedin.com/in/jonathandpolansky" class="image avatar" target="_blank"><img src="images/avatar.jpg" alt="" /></a>
                <h1>I am <strong>Jonathan Polansky</strong>. <br />
                Welcome to my blog!</h1>
            </div>
        </header>
        <div id="main">
            <section id="editDelete">
                <button id="editButton" class="button" onclick="editPost()">Edit Post</button>
                <button id="deleteButton" class="button" onclick="deletePost()">Delete Post</button>
                <input type="text" id="titleField" style="margin: 1em;">
                <input type="text" id="descriptionField" style="margin: 1em;">
                <div id="editPostBox"></div>
                <button id="saveEditButton" class="button" onclick="editPostSave()">Save Post</button>
            </section>
            <section id="fullBlogPost">
                {post['html']}
            </section>
            <section id="commentSection">
					<h2 style="text-align: center;">Comments</h2>
					<div id="comments"></div>
					<button id="newComment" class="button" onclick="commentCreate()">Add Comment</button>
					<form id="newCommentForm">
						<input type="text" id="commentBox" placeholder="Type here..." style="margin: 1em;" required>
					</form>
					<button id="submitComment" class="button" onclick="commentSubmit()">Save</button>
				</section>
        </div>
        <footer id="footer">
            <div class="inner">
                <ul class="icons">
                    <li><a href="https://www.linkedin.com/in/jonathandpolansky/" class="icon brands fa-linkedin" target="_blank"><span class="label">LinkedIn</span></a></li>
                    <li><a href="https://github.com/jdplab" class="icon brands fa-github" target="_blank"><span class="label">Github</span></a></li>
                    <li><a href="mailto:jon@jon-polansky.com" class="icon solid fa-envelope" target="_blank"><span class="label">Email</span></a></li>
                </ul>
                <ul class="visitorcount">
                    <li><span>Your Visits: <b id="visits">Loading...</b></span></li>
                    <li><span>Unique Visitors: <b id="unique_visitors">Loading...</b></span></li>
                    <li><span>Total Website Visitors: <b id="total_visits">Loading...</b></span></li>
                </ul>
            </div>
        </footer>

        <script src="assets/js/jquery.min.js"></script>
        <script src="assets/js/jquery.poptrox.min.js"></script>
        <script src="assets/js/browser.min.js"></script>
        <script src="assets/js/breakpoints.min.js"></script>
        <script src="assets/js/util.js"></script>
        <script src="assets/js/menu.js"></script>
        <script src="assets/js/scroll.js"></script>
        <script src="assets/js/modal.js"></script>
        <script src="assets/js/visitorcount.js"></script>
        <script src="assets/js/auth.js"></script>
        <script src="assets/js/displayblogpost.js"></script>
        <script src="assets/js/main.js"></script>
    </body>
</html>
"""