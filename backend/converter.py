import io


# Summary (optional)
if schema.get("summary"):
doc.add_heading("Summary", level=1)
doc.add_paragraph(schema["summary"]) # type: ignore


# Sections
def add_section(title: str, lines: List[str]):
if not lines:
return
doc.add_heading(title, level=1)
for ln in lines:
doc.add_paragraph(ln)


add_section("Experience", schema.get("experience", []))
add_section("Education", schema.get("education", []))
add_section("Skills", schema.get("skills", []))
add_section("Certifications", schema.get("certs", []))


bio = io.BytesIO()
doc.save(bio)
bio.seek(0)
return bio.getvalue()




def convert_to_standard_docx(file_bytes: bytes, filename: str, content_type: str) -> Tuple[bytes, str]:
# 1) Extract text
if content_type == "application/pdf":
text = _extract_text_from_pdf(file_bytes)
elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
text = _extract_text_from_docx(file_bytes)
else:
raise ValueError("Only PDF or DOCX supported.")


lines = _clean_lines(text)


# 2) Basic fields
full_text = "\n".join(lines)
name = _guess_name(lines)
email = _find_field(EMAIL_RE, full_text)
phone = _find_field(PHONE_RE, full_text)


# 3) Primitive section split (you can refine later)
sections = _split_sections(lines)


schema = {
"name": name,
"email": email,
"phone": phone,
"summary": "", # optional: add rules to detect a summary paragraph
"experience": sections.get("experience", []),
"education": sections.get("education", []),
"skills": sections.get("skills", []),
"certs": sections.get("certs", []),
}


# 4) Render DOCX
out = _render_docx(schema)


safe_base = re.sub(r"\.(pdf|docx)$", "", filename, flags=re.I)
out_name = f"{safe_base}_STANDARD.docx"
return out, out_name
