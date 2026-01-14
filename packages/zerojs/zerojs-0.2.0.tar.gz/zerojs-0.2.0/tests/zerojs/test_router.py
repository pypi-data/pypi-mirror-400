"""Tests for file-based routing."""

from pathlib import Path

from zerojs.router import file_to_route, scan_pages


class TestFileToRoute:
    """Tests for file_to_route function."""

    def test_index_file_maps_to_root(self, tmp_path: Path) -> None:
        """pages/index.html → /"""
        pages_dir = tmp_path / "pages"
        pages_dir.mkdir()
        index_file = pages_dir / "index.html"
        index_file.touch()

        route = file_to_route(index_file, pages_dir)

        assert route.url_path == "/"
        assert route.params == []

    def test_simple_page_maps_to_path(self, tmp_path: Path) -> None:
        """pages/about.html → /about"""
        pages_dir = tmp_path / "pages"
        pages_dir.mkdir()
        about_file = pages_dir / "about.html"
        about_file.touch()

        route = file_to_route(about_file, pages_dir)

        assert route.url_path == "/about"
        assert route.params == []

    def test_nested_index_maps_to_directory(self, tmp_path: Path) -> None:
        """pages/users/index.html → /users"""
        pages_dir = tmp_path / "pages"
        users_dir = pages_dir / "users"
        users_dir.mkdir(parents=True)
        index_file = users_dir / "index.html"
        index_file.touch()

        route = file_to_route(index_file, pages_dir)

        assert route.url_path == "/users"
        assert route.params == []

    def test_dynamic_route_extracts_param(self, tmp_path: Path) -> None:
        """pages/users/[id].html → /users/{id}"""
        pages_dir = tmp_path / "pages"
        users_dir = pages_dir / "users"
        users_dir.mkdir(parents=True)
        user_file = users_dir / "[id].html"
        user_file.touch()

        route = file_to_route(user_file, pages_dir)

        assert route.url_path == "/users/{id}"
        assert route.params == ["id"]

    def test_multiple_dynamic_params(self, tmp_path: Path) -> None:
        """pages/blog/[slug]/comments/[id].html → /blog/{slug}/comments/{id}"""
        pages_dir = tmp_path / "pages"
        comments_dir = pages_dir / "blog" / "[slug]" / "comments"
        comments_dir.mkdir(parents=True)
        comment_file = comments_dir / "[id].html"
        comment_file.touch()

        route = file_to_route(comment_file, pages_dir)

        assert route.url_path == "/blog/{slug}/comments/{id}"
        assert route.params == ["slug", "id"]

    def test_deeply_nested_static_route(self, tmp_path: Path) -> None:
        """pages/docs/api/v1/users.html → /docs/api/v1/users"""
        pages_dir = tmp_path / "pages"
        nested_dir = pages_dir / "docs" / "api" / "v1"
        nested_dir.mkdir(parents=True)
        users_file = nested_dir / "users.html"
        users_file.touch()

        route = file_to_route(users_file, pages_dir)

        assert route.url_path == "/docs/api/v1/users"
        assert route.params == []

    def test_context_file_detected_for_dynamic_route(self, tmp_path: Path) -> None:
        """[id].html should detect _id.py as context file."""
        pages_dir = tmp_path / "pages"
        users_dir = pages_dir / "users"
        users_dir.mkdir(parents=True)

        user_file = users_dir / "[id].html"
        user_file.touch()
        context_file = users_dir / "_id.py"
        context_file.touch()

        route = file_to_route(user_file, pages_dir)

        assert route.context_file == context_file

    def test_context_file_detected_for_static_route(self, tmp_path: Path) -> None:
        """about.html should detect _about.py as context file."""
        pages_dir = tmp_path / "pages"
        pages_dir.mkdir()

        about_file = pages_dir / "about.html"
        about_file.touch()
        context_file = pages_dir / "_about.py"
        context_file.touch()

        route = file_to_route(about_file, pages_dir)

        assert route.context_file == context_file

    def test_no_context_file_when_missing(self, tmp_path: Path) -> None:
        """No context_file when .py file doesn't exist."""
        pages_dir = tmp_path / "pages"
        pages_dir.mkdir()

        about_file = pages_dir / "about.html"
        about_file.touch()

        route = file_to_route(about_file, pages_dir)

        assert route.context_file is None


class TestScanPages:
    """Tests for scan_pages function."""

    def test_empty_directory_returns_empty_list(self, tmp_path: Path) -> None:
        """Empty pages dir returns no routes."""
        pages_dir = tmp_path / "pages"
        pages_dir.mkdir()

        routes = scan_pages(pages_dir)

        assert routes == []

    def test_nonexistent_directory_returns_empty_list(self, tmp_path: Path) -> None:
        """Nonexistent pages dir returns no routes."""
        pages_dir = tmp_path / "nonexistent"

        routes = scan_pages(pages_dir)

        assert routes == []

    def test_scans_all_html_files(self, tmp_path: Path) -> None:
        """Finds all HTML files in directory tree."""
        pages_dir = tmp_path / "pages"
        pages_dir.mkdir()

        (pages_dir / "index.html").touch()
        (pages_dir / "about.html").touch()
        users_dir = pages_dir / "users"
        users_dir.mkdir()
        (users_dir / "index.html").touch()
        (users_dir / "[id].html").touch()

        routes = scan_pages(pages_dir)

        assert len(routes) == 4
        url_paths = {r.url_path for r in routes}
        assert url_paths == {"/", "/about", "/users", "/users/{id}"}

    def test_static_routes_sorted_before_dynamic(self, tmp_path: Path) -> None:
        """Static routes should come before dynamic routes."""
        pages_dir = tmp_path / "pages"
        users_dir = pages_dir / "users"
        users_dir.mkdir(parents=True)

        (users_dir / "[id].html").touch()
        (users_dir / "index.html").touch()

        routes = scan_pages(pages_dir)

        assert routes[0].url_path == "/users"
        assert routes[1].url_path == "/users/{id}"

    def test_ignores_unsupported_files(self, tmp_path: Path) -> None:
        """Only supported file types (.html, .txt, .md) are scanned."""
        pages_dir = tmp_path / "pages"
        pages_dir.mkdir()

        (pages_dir / "index.html").touch()
        (pages_dir / "_index.py").touch()
        (pages_dir / "style.css").touch()  # Not supported
        (pages_dir / "data.json").touch()  # Not supported

        routes = scan_pages(pages_dir)

        assert len(routes) == 1
        assert routes[0].url_path == "/"

    def test_scans_txt_and_md_files(self, tmp_path: Path) -> None:
        """Text and markdown files are scanned as static routes."""
        pages_dir = tmp_path / "pages"
        pages_dir.mkdir()

        (pages_dir / "robots.txt").write_text("User-agent: *")
        (pages_dir / "readme.md").write_text("# Hello")
        (pages_dir / "index.html").touch()

        routes = scan_pages(pages_dir)

        assert len(routes) == 3

        # Find each route
        txt_route = next(r for r in routes if r.url_path == "/robots.txt")
        md_route = next(r for r in routes if r.url_path == "/readme.md")
        html_route = next(r for r in routes if r.url_path == "/")

        assert txt_route.is_static is True
        assert md_route.is_static is True
        assert html_route.is_static is False
