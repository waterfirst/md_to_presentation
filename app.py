import streamlit as st
import re
import base64
from pathlib import Path

# Try to import markdown, but have a fallback method
try:
    import markdown
    
    def convert_md_to_html(md_content):
        """Convert markdown to HTML using the markdown package"""
        return markdown.markdown(md_content, extensions=['extra', 'codehilite', 'tables'])
        
except ImportError:
    # Fallback simple markdown to HTML converter
    def convert_md_to_html(md_content):
        """Simple markdown to HTML converter as fallback"""
        html_content = md_content
        
        # Convert headers
        html_content = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
        
        # Handle table of contents format (numbered list with links on a single line)
        toc_pattern = r'([0-9]+)\. \[(.*?)\]\((.*?)\)'
        if re.search(toc_pattern, html_content):
            # If contents is detected, put each item on a new line before processing
            content_with_breaks = ""
            for line in html_content.split('\n'):
                if re.search(toc_pattern, line):
                    # Separate numbered list items
                    items = re.findall(r'([0-9]+)\. \[(.*?)\]\((.*?)\)', line)
                    if items:
                        for item in items:
                            content_with_breaks += f"{item[0]}. [{item[1]}]({item[2]})\n"
                        content_with_breaks += "\n"
                    else:
                        content_with_breaks += line + "\n"
                else:
                    content_with_breaks += line + "\n"
            
            html_content = content_with_breaks
        
        # Convert numbered lists (must come before regular paragraph conversion)
        list_items = []
        in_list = False
        
        new_content = []
        for line in html_content.split('\n'):
            # Match numbered list pattern
            match = re.match(r'([0-9]+)\. (.*?)', line)
            if match:
                if not in_list:
                    new_content.append('<ol>')
                    in_list = True
                # Convert any markdown links in list items
                item_content = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', match.group(2))
                new_content.append(f'<li>{item_content}</li>')
            else:
                if in_list:
                    new_content.append('</ol>')
                    in_list = False
                new_content.append(line)
        
        if in_list:
            new_content.append('</ol>')
            
        html_content = '\n'.join(new_content)
        
        # Convert links (that aren't already converted in lists)
        html_content = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', html_content)
        
        # Convert paragraphs (lines followed by blank lines)
        html_content = re.sub(r'([^\n]+)\n\n', r'<p>\1</p>\n\n', html_content)
        
        # Convert bold
        html_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_content)
        
        # Convert italic
        html_content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html_content)
        
        # Convert unordered lists
        list_items = []
        in_list = False
        
        new_content = []
        for line in html_content.split('\n'):
            match = re.match(r'- (.*?)', line)
            if match:
                if not in_list:
                    new_content.append('<ul>')
                    in_list = True
                new_content.append(f'<li>{match.group(1)}</li>')
            else:
                if in_list:
                    new_content.append('</ul>')
                    in_list = False
                new_content.append(line)
        
        if in_list:
            new_content.append('</ul>')
            
        html_content = '\n'.join(new_content)
        
        # Convert code blocks
        html_content = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', html_content, flags=re.DOTALL)
        
        # Convert inline code
        html_content = re.sub(r'`(.*?)`', r'<code>\1</code>', html_content)
        
        return html_content

def md_to_html_presentation(md_content, theme="white", transition="slide", max_chars_per_slide=1500, max_paragraphs_per_slide=6, 
                      h1_size=48, h2_size=36, body_size=24):
    """
    Convert markdown content to HTML presentation format using reveal.js
    Split long content into vertical slides
    """
    # Convert markdown to HTML
    html_content = convert_md_to_html(md_content)
    
    # Split the HTML content by heading tags to create slides
    # First, add markers to the headings to facilitate splitting
    marked_content = re.sub(r'<h1[^>]*>(.*?)</h1>', r'%%%SLIDE%%%<h1>\1</h1>', html_content)
    marked_content = re.sub(r'<h2[^>]*>(.*?)</h2>', r'%%%SLIDE%%%<h2>\1</h2>', marked_content)
    
    # Split by the marker
    slides = marked_content.split('%%%SLIDE%%%')
    
    # Remove empty first slide if needed
    if slides[0].strip() == '':
        slides.pop(0)
    else:
        # If there's content before the first heading, make it an intro slide
        slides[0] = f'<h1>소개</h1>{slides[0]}'
    
    # Create the slides HTML with subslides for long content
    slides_html = ""
    for slide in slides:
        if not slide.strip():  # Skip empty slides
            continue
            
        # Extract the heading to be repeated across vertical slides
        heading_match = re.search(r'<h[1-2][^>]*>(.*?)</h[1-2]>', slide)
        heading = heading_match.group(0) if heading_match else '<h2>슬라이드</h2>'
        
        # Handle long slides by splitting them into vertical slides
        content_parts = []
        
        # Extract paragraph-like elements and blocks
        heading_pattern = r'<h[1-6][^>]*>.*?</h[1-6]>'
        paragraph_pattern = r'<p>.*?</p>'
        list_pattern = r'<[ou]l>.*?</[ou]l>'
        table_pattern = r'<table>.*?</table>'
        pre_pattern = r'<pre>.*?</pre>'
        
        # Get rid of the heading for content processing
        content_without_heading = re.sub(heading_pattern, '', slide, count=1)
        
        # Find all blocks: paragraphs, lists, tables, code blocks
        blocks = []
        # Find all paragraph blocks
        blocks.extend(re.findall(paragraph_pattern, content_without_heading, re.DOTALL))
        # Find all list blocks
        blocks.extend(re.findall(list_pattern, content_without_heading, re.DOTALL))
        # Find all table blocks
        blocks.extend(re.findall(table_pattern, content_without_heading, re.DOTALL))
        # Find all code blocks
        blocks.extend(re.findall(pre_pattern, content_without_heading, re.DOTALL))
        
        # If we couldn't properly split it into blocks, just use the whole content
        if not blocks:
            blocks = [content_without_heading]
        
        # Initialize with the heading
        current_part = heading
        current_size = len(heading)
        current_paragraphs = 0
        
        # Distribute blocks across slides
        for block in blocks:
            block_size = len(block)
            
            # Check if adding this block would exceed our limits
            if (current_size + block_size > max_chars_per_slide or 
                current_paragraphs >= max_paragraphs_per_slide) and current_size > len(heading):
                # Save current part and start a new one with the heading
                content_parts.append(current_part)
                current_part = heading
                current_size = len(heading)
                current_paragraphs = 0
            
            # Add the block to the current part
            current_part += block
            current_size += block_size
            current_paragraphs += 1
        
        # Add the last part if it has content beyond just the heading
        if current_size > len(heading):
            content_parts.append(current_part)
        
        # If we have multiple parts, create vertical slides
        if len(content_parts) > 1:
            slides_html += '<section>'
            for part in content_parts:
                slides_html += f'<section>{part}</section>'
            slides_html += '</section>'
        else:
            # Single slide, no need for vertical slides
            slides_html += f'<section>{slide}</section>'
    
    # Create the complete HTML presentation
    presentation_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Presentation</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.1.0/dist/reset.css">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.1.0/dist/reveal.css">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.1.0/dist/theme/{theme}.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/default.min.css">
        <style>
            .reveal section {{
                text-align: left;
                height: 100%;
                overflow: auto;
                padding: 20px;
            }}
            
            /* 한글 폰트 최적화 */
            .reveal h1 {{
                font-size: {h1_size}px;
                font-weight: 600;
                margin-bottom: 0.6em;
                line-height: 1.2;
            }}
            
            .reveal h2 {{
                font-size: {h2_size}px;
                font-weight: 600;
                margin-bottom: 0.5em;
                line-height: 1.2;
            }}
            
            .reveal h3 {{
                font-size: {int(h2_size * 0.8)}px;
                font-weight: 600;
                margin-bottom: 0.4em;
            }}
            
            .reveal p, .reveal li, .reveal td, .reveal th {{
                font-size: {body_size}px;
                line-height: 1.4;
            }}
            
            .reveal code {{
                font-size: {int(body_size * 0.9)}px;
                font-family: 'Consolas', 'Monaco', monospace;
            }}
            
            /* 슬라이드 내용의 최대 크기 제한 */
            .reveal .slides {{
                height: 100%;
            }}
            
            /* 네비게이션 화살표 스타일 */
            .reveal .controls {{
                bottom: 16px;
                right: 16px;
            }}
            
            /* 하위 슬라이드를 위한 아래 화살표 더 눈에 띄게 */
            .reveal .controls .navigate-down.enabled {{
                opacity: 0.9;
                animation: pulse 2s infinite;
            }}
            
            @keyframes pulse {{
                0% {{ opacity: 0.5; }}
                50% {{ opacity: 1; }}
                100% {{ opacity: 0.5; }}
            }}
            .reveal ul, .reveal ol {{
                display: block;
            }}
            .reveal pre {{
                width: 100%;
                box-shadow: none;
                font-size: {int(body_size * 0.9)}px;
            }}
            .reveal table {{
                margin: 1em 0;
                width: 100%;
            }}
            .reveal th, .reveal td {{
                padding: 0.5em;
                border: 1px solid #ccc;
            }}
        </style>
    </head>
    <body>
        <div class="reveal">
            <div class="slides">
                {slides_html}
            </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/reveal.js@4.1.0/dist/reveal.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js"></script>
        <script>
            Reveal.initialize({{
                hash: true,
                slideNumber: true,
                transition: '{transition}',
                center: false,
                plugins: [ ],
                highlightConfig: {{
                    tabReplace: '    '
                }},
                // 이중 슬라이드 (상하 이동) 활성화
                navigationMode: 'default',
                // 아래로 이동하는 화살표 표시
                controlsLayout: 'bottom-right',
                controlsTutorial: true,
                // 진행 표시기 (상단에 점으로 표시)
                progress: true,
                // 네비게이션 도움말 표시
                help: true
            }});
            
            // Initialize syntax highlighting
            document.querySelectorAll('pre code').forEach((block) => {{
                hljs.highlightBlock(block);
            }});
        </script>
    </body>
    </html>
    """
    
    return presentation_html

def get_download_link(content, filename, text):
    """Generate a download link for the file content"""
    b64 = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:file/html;base64,{b64}" download="{filename}" class="download-btn">{text}</a>'
    return href

def extract_slide_titles(html_content):
    """Extract slide titles from the HTML content"""
    # 정규식으로 슬라이드 섹션 추출
    section_pattern = r'<section>(.*?)</section>'
    all_sections = re.findall(section_pattern, html_content, re.DOTALL)
    
    titles = []
    for section in all_sections:
        # 중첩된 섹션인지 확인 (수직 슬라이드가 있는지)
        nested_sections = re.findall(r'<section>(.*?)</section>', section, re.DOTALL)
        
        # 중첩 슬라이드가 있으면
        if nested_sections and len(nested_sections) > 0:
            # 첫 번째 중첩 슬라이드에서 제목 추출
            heading_match = re.search(r'<h[1-2][^>]*>(.*?)</h[1-2]>', nested_sections[0])
            if heading_match:
                title = heading_match.group(1)
                titles.append(title)
                # 하위 슬라이드 수 표시
                slide_count = len(nested_sections)
                if slide_count > 1:
                    titles[-1] += f" ({slide_count}페이지)"
        else:
            # 단일 슬라이드에서 제목 추출
            heading_match = re.search(r'<h[1-2][^>]*>(.*?)</h[1-2]>', section)
            if heading_match:
                titles.append(heading_match.group(1))
    
    return titles

def main():
    st.set_page_config(page_title="MD to HTML Presentation Converter", 
                       page_icon="📊", 
                       layout="wide")
    
    st.title("마크다운 프레젠테이션 변환기")
    st.subheader("AI로 받은 보고서를 프레젠테이션으로 변환하세요")
    
    with st.expander("사용 방법", expanded=True):
        st.markdown("""
        1. **마크다운 파일 업로드 또는 텍스트 입력**: `.md` 확장자의 마크다운 파일을 업로드하거나 직접 마크다운 텍스트를 입력하세요
        2. **변환**: 내용이 자동으로 HTML 프레젠테이션 형식으로 변환됩니다
        3. **미리보기**: 변환된 프레젠테이션을 미리 볼 수 있습니다
        4. **다운로드**: HTML 파일을 다운로드하여 브라우저에서 열 수 있습니다
        
        **참고**: 최상의 결과를 위해 마크다운 내용은 `#` 또는 `##` 제목으로 구조화되어 있어야 합니다. 각 제목은 새로운 슬라이드가 됩니다.
        """)
    
    # Add tabs for file upload and text input
    tab1, tab2 = st.tabs(["파일 업로드", "텍스트 입력"])
    
    # Variables to store the content and filename
    md_content = None
    file_name = "presentation.html"
    
    with tab1:
        uploaded_file = st.file_uploader("마크다운 파일을 업로드하세요", type=['md'])
        if uploaded_file is not None:
            md_content = uploaded_file.read().decode()
            file_name = Path(uploaded_file.name).stem + "_presentation.html"
    
    with tab2:
        md_text_input = st.text_area("마크다운 텍스트를 입력하세요", height=300, 
                                     placeholder="# 제목\n\n내용을 입력하세요...\n\n## 소제목\n\n- 항목 1\n- 항목 2")
        if md_text_input and uploaded_file is None:
            md_content = md_text_input
    
    # Theme and transition options
    col1, col2 = st.columns(2)
    with col1:
        theme = st.selectbox(
            "프레젠테이션 테마",
            ["white", "black", "league", "beige", "sky", "night", "serif", "simple", "solarized", "moon", "dracula"]
        )
    with col2:
        transition = st.selectbox(
            "슬라이드 전환 효과",
            ["none", "fade", "slide", "convex", "concave", "zoom"]
        )
        
    # 슬라이드 분할 설정    
    st.subheader("슬라이드 분할 설정")
    st.info("긴 내용은 자동으로 여러 하위 슬라이드로 분할됩니다. 아래 화살표로 이동할 수 있습니다.")
    
    col3, col4 = st.columns(2)
    with col3:
        max_chars = st.slider("슬라이드당 최대 글자 수", 500, 3000, 1500, 100,
                            help="이 글자 수를 초과하면 내용이 다음 하위 슬라이드로 이동import streamlit as st
import re
import base64
from pathlib import Path

# Try to import markdown, but have a fallback method
try:
    import markdown
    
    def convert_md_to_html(md_content):
        """Convert markdown to HTML using the markdown package"""
        return markdown.markdown(md_content, extensions=['extra', 'codehilite', 'tables'])
        
except ImportError:
    # Fallback simple markdown to HTML converter
    def convert_md_to_html(md_content):
        """Simple markdown to HTML converter as fallback"""
        html_content = md_content
        
        # Convert headers
        html_content = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
        
        # Handle table of contents format (numbered list with links on a single line)
        toc_pattern = r'([0-9]+)\. \[(.*?)\]\((.*?)\)'
        if re.search(toc_pattern, html_content):
            # If contents is detected, put each item on a new line before processing
            content_with_breaks = ""
            for line in html_content.split('\n'):
                if re.search(toc_pattern, line):
                    # Separate numbered list items
                    items = re.findall(r'([0-9]+)\. \[(.*?)\]\((.*?)\)', line)
                    if items:
                        for item in items:
                            content_with_breaks += f"{item[0]}. [{item[1]}]({item[2]})\n"
                        content_with_breaks += "\n"
                    else:
                        content_with_breaks += line + "\n"
                else:
                    content_with_breaks += line + "\n"
            
            html_content = content_with_breaks
        
        # Convert numbered lists (must come before regular paragraph conversion)
        list_items = []
        in_list = False
        
        new_content = []
        for line in html_content.split('\n'):
            # Match numbered list pattern
            match = re.match(r'([0-9]+)\. (.*?)', line)
            if match:
                if not in_list:
                    new_content.append('<ol>')
                    in_list = True
                # Convert any markdown links in list items
                item_content = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', match.group(2))
                new_content.append(f'<li>{item_content}</li>')
            else:
                if in_list:
                    new_content.append('</ol>')
                    in_list = False
                new_content.append(line)
        
        if in_list:
            new_content.append('</ol>')
            
        html_content = '\n'.join(new_content)
        
        # Convert links (that aren't already converted in lists)
        html_content = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', html_content)
        
        # Convert paragraphs (lines followed by blank lines)
        html_content = re.sub(r'([^\n]+)\n\n', r'<p>\1</p>\n\n', html_content)
        
        # Convert bold
        html_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_content)
        
        # Convert italic
        html_content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html_content)
        
        # Convert unordered lists
        list_items = []
        in_list = False
        
        new_content = []
        for line in html_content.split('\n'):
            match = re.match(r'- (.*?)', line)
            if match:
                if not in_list:
                    new_content.append('<ul>')
                    in_list = True
                new_content.append(f'<li>{match.group(1)}</li>')
            else:
                if in_list:
                    new_content.append('</ul>')
                    in_list = False
                new_content.append(line)
        
        if in_list:
            new_content.append('</ul>')
            
        html_content = '\n'.join(new_content)
        
        # Convert code blocks
        html_content = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', html_content, flags=re.DOTALL)
        
        # Convert inline code
        html_content = re.sub(r'`(.*?)`', r'<code>\1</code>', html_content)
        
        return html_content

def md_to_html_presentation(md_content, theme="white", transition="slide", max_chars_per_slide=1500, max_paragraphs_per_slide=6, 
                      h1_size=48, h2_size=36, body_size=24):
    """
    Convert markdown content to HTML presentation format using reveal.js
    Split long content into vertical slides
    """
    # Convert markdown to HTML
    html_content = convert_md_to_html(md_content)
    
    # Split the HTML content by heading tags to create slides
    # First, add markers to the headings to facilitate splitting
    marked_content = re.sub(r'<h1[^>]*>(.*?)</h1>', r'%%%SLIDE%%%<h1>\1</h1>', html_content)
    marked_content = re.sub(r'<h2[^>]*>(.*?)</h2>', r'%%%SLIDE%%%<h2>\1</h2>', marked_content)
    
    # Split by the marker
    slides = marked_content.split('%%%SLIDE%%%')
    
    # Remove empty first slide if needed
    if slides[0].strip() == '':
        slides.pop(0)
    else:
        # If there's content before the first heading, make it an intro slide
        slides[0] = f'<h1>소개</h1>{slides[0]}'
    
    # Create the slides HTML with subslides for long content
    slides_html = ""
    for slide in slides:
        if not slide.strip():  # Skip empty slides
            continue
            
        # Extract the heading to be repeated across vertical slides
        heading_match = re.search(r'<h[1-2][^>]*>(.*?)</h[1-2]>', slide)
        heading = heading_match.group(0) if heading_match else '<h2>슬라이드</h2>'
        
        # Handle long slides by splitting them into vertical slides
        content_parts = []
        
        # Extract paragraph-like elements and blocks
        heading_pattern = r'<h[1-6][^>]*>.*?</h[1-6]>'
        paragraph_pattern = r'<p>.*?</p>'
        list_pattern = r'<[ou]l>.*?</[ou]l>'
        table_pattern = r'<table>.*?</table>'
        pre_pattern = r'<pre>.*?</pre>'
        
        # Get rid of the heading for content processing
        content_without_heading = re.sub(heading_pattern, '', slide, count=1)
        
        # Find all blocks: paragraphs, lists, tables, code blocks
        blocks = []
        # Find all paragraph blocks
        blocks.extend(re.findall(paragraph_pattern, content_without_heading, re.DOTALL))
        # Find all list blocks
        blocks.extend(re.findall(list_pattern, content_without_heading, re.DOTALL))
        # Find all table blocks
        blocks.extend(re.findall(table_pattern, content_without_heading, re.DOTALL))
        # Find all code blocks
        blocks.extend(re.findall(pre_pattern, content_without_heading, re.DOTALL))
        
        # If we couldn't properly split it into blocks, just use the whole content
        if not blocks:
            blocks = [content_without_heading]
        
        # Initialize with the heading
        current_part = heading
        current_size = len(heading)
        current_paragraphs = 0
        
        # Distribute blocks across slides
        for block in blocks:
            block_size = len(block)
            
            # Check if adding this block would exceed our limits
            if (current_size + block_size > max_chars_per_slide or 
                current_paragraphs >= max_paragraphs_per_slide) and current_size > len(heading):
                # Save current part and start a new one with the heading
                content_parts.append(current_part)
                current_part = heading
                current_size = len(heading)
                current_paragraphs = 0
            
            # Add the block to the current part
            current_part += block
            current_size += block_size
            current_paragraphs += 1
        
        # Add the last part if it has content beyond just the heading
        if current_size > len(heading):
            content_parts.append(current_part)
        
        # If we have multiple parts, create vertical slides
        if len(content_parts) > 1:
            slides_html += '<section>'
            for part in content_parts:
                slides_html += f'<section>{part}</section>'
            slides_html += '</section>'
        else:
            # Single slide, no need for vertical slides
            slides_html += f'<section>{slide}</section>'
    
    # Create the complete HTML presentation
    presentation_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Presentation</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.1.0/dist/reset.css">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.1.0/dist/reveal.css">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.1.0/dist/theme/{theme}.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/default.min.css">
        <style>
            .reveal section {{
                text-align: left;
                height: 100%;
                overflow: auto;
                padding: 20px;
            }}
            
            /* 한글 폰트 최적화 */
            .reveal h1 {{
                font-size: {h1_size}px;
                font-weight: 600;
                margin-bottom: 0.6em;
                line-height: 1.2;
            }}
            
            .reveal h2 {{
                font-size: {h2_size}px;
                font-weight: 600;
                margin-bottom: 0.5em;
                line-height: 1.2;
            }}
            
            .reveal h3 {{
                font-size: {int(h2_size * 0.8)}px;
                font-weight: 600;
                margin-bottom: 0.4em;
            }}
            
            .reveal p, .reveal li, .reveal td, .reveal th {{
                font-size: {body_size}px;
                line-height: 1.4;
            }}
            
            .reveal code {{
                font-size: {int(body_size * 0.9)}px;
                font-family: 'Consolas', 'Monaco', monospace;
            }}
            
            /* 슬라이드 내용의 최대 크기 제한 */
            .reveal .slides {{
                height: 100%;
            }}
            
            /* 네비게이션 화살표 스타일 */
            .reveal .controls {{
                bottom: 16px;
                right: 16px;
            }}
            
            /* 하위 슬라이드를 위한 아래 화살표 더 눈에 띄게 */
            .reveal .controls .navigate-down.enabled {{
                opacity: 0.9;
                animation: pulse 2s infinite;
            }}
            
            @keyframes pulse {{
                0% {{ opacity: 0.5; }}
                50% {{ opacity: 1; }}
                100% {{ opacity: 0.5; }}
            }}
            .reveal ul, .reveal ol {{
                display: block;
            }}
            .reveal pre {{
                width: 100%;
                box-shadow: none;
                font-size: {int(body_size * 0.9)}px;
            }}
            .reveal table {{
                margin: 1em 0;
                width: 100%;
            }}
            .reveal th, .reveal td {{
                padding: 0.5em;
                border: 1px solid #ccc;
            }}
        </style>
    </head>
    <body>
        <div class="reveal">
            <div class="slides">
                {slides_html}
            </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/reveal.js@4.1.0/dist/reveal.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js"></script>
        <script>
            Reveal.initialize({{
                hash: true,
                slideNumber: true,
                transition: '{transition}',
                center: false,
                plugins: [ ],
                highlightConfig: {{
                    tabReplace: '    '
                }},
                // 이중 슬라이드 (상하 이동) 활성화
                navigationMode: 'default',
                // 아래로 이동하는 화살표 표시
                controlsLayout: 'bottom-right',
                controlsTutorial: true,
                // 진행 표시기 (상단에 점으로 표시)
                progress: true,
                // 네비게이션 도움말 표시
                help: true
            }});
            
            // Initialize syntax highlighting
            document.querySelectorAll('pre code').forEach((block) => {{
                hljs.highlightBlock(block);
            }});
        </script>
    </body>
    </html>
    """
    
    return presentation_html

def get_download_link(content, filename, text):
    """Generate a download link for the file content"""
    b64 = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:file/html;base64,{b64}" download="{filename}" class="download-btn">{text}</a>'
    return href

def extract_slide_titles(html_content):
    """Extract slide titles from the HTML content"""
    # 정규식으로 슬라이드 섹션 추출
    section_pattern = r'<section>(.*?)</section>'
    all_sections = re.findall(section_pattern, html_content, re.DOTALL)
    
    titles = []
    for section in all_sections:
        # 중첩된 섹션인지 확인 (수직 슬라이드가 있는지)
        nested_sections = re.findall(r'<section>(.*?)</section>', section, re.DOTALL)
        
        # 중첩 슬라이드가 있으면
        if nested_sections and len(nested_sections) > 0:
            # 첫 번째 중첩 슬라이드에서 제목 추출
            heading_match = re.search(r'<h[1-2][^>]*>(.*?)</h[1-2]>', nested_sections[0])
            if heading_match:
                title = heading_match.group(1)
                titles.append(title)
                # 하위 슬라이드 수 표시
                slide_count = len(nested_sections)
                if slide_count > 1:
                    titles[-1] += f" ({slide_count}페이지)"
        else:
            # 단일 슬라이드에서 제목 추출
            heading_match = re.search(r'<h[1-2][^>]*>(.*?)</h[1-2]>', section)
            if heading_match:
                titles.append(heading_match.group(1))
    
    return titles

def main():
    st.set_page_config(page_title="MD to HTML Presentation Converter", 
                       page_icon="📊", 
                       layout="wide")
    
    st.title("마크다운 프레젠테이션 변환기")
    st.subheader("AI로 받은 보고서를 프레젠테이션으로 변환하세요")
    
    with st.expander("사용 방법", expanded=True):
        st.markdown("""
        1. **마크다운 파일 업로드 또는 텍스트 입력**: `.md` 확장자의 마크다운 파일을 업로드하거나 직접 마크다운 텍스트를 입력하세요
        2. **변환**: 내용이 자동으로 HTML 프레젠테이션 형식으로 변환됩니다
        3. **미리보기**: 변환된 프레젠테이션을 미리 볼 수 있습니다
        4. **다운로드**: HTML 파일을 다운로드하여 브라우저에서 열 수 있습니다
        
        **참고**: 최상의 결과를 위해 마크다운 내용은 `#` 또는 `##` 제목으로 구조화되어 있어야 합니다. 각 제목은 새로운 슬라이드가 됩니다.
        """)
    
    # Add tabs for file upload and text input
    tab1, tab2 = st.tabs(["파일 업로드", "텍스트 입력"])
    
    # Variables to store the content and filename
    md_content = None
    file_name = "presentation.html"
    
    with tab1:
        uploaded_file = st.file_uploader("마크다운 파일을 업로드하세요", type=['md'])
        if uploaded_file is not None:
            md_content = uploaded_file.read().decode()
            file_name = Path(uploaded_file.name).stem + "_presentation.html"
    
    with tab2:
        md_text_input = st.text_area("마크다운 텍스트를 입력하세요", height=300, 
                                     placeholder="# 제목\n\n내용을 입력하세요...\n\n## 소제목\n\n- 항목 1\n- 항목 2")
        if md_text_input and uploaded_file is None:
            md_content = md_text_input
    
    # Theme and transition options
    col1, col2 = st.columns(2)
    with col1:
        theme = st.selectbox(
            "프레젠테이션 테마",
            ["white", "black", "league", "beige", "sky", "night", "serif", "simple", "solarized", "moon", "dracula"]
        )
    with col2:
        transition = st.selectbox(
            "슬라이드 전환 효과",
            ["none", "fade", "slide", "convex", "concave", "zoom"]
        )
        
    # 슬라이드 분할 설정    
    st.subheader("슬라이드 분할 설정")
    st.info("긴 내용은 자동으로 여러 하위 슬라이드로 분할됩니다. 아래 화살표로 이동할 수 있습니다.")
    
    col3, col4 = st.columns(2)
    with col3:
        max_chars = st.slider("슬라이드당 최대 글자 수", 500, 3000, 1500, 100,
                            help="이 글자 수를 초과하면 내용이 다음 하위 슬라이드로 이동
