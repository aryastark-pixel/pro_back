from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView
from rest_framework import status
from .models import Name
from .serializers import *
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_LEFT
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Citizen
import json
from io import BytesIO
# Create your views here.


class CitizenCreateAPIView(APIView):
    def post(self, request):
        serializer = CitizenSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CitizenByAadhaarAPIView(RetrieveAPIView):
    queryset = Citizen.objects.all()
    serializer_class = CitizenSerializer
    lookup_field = "aadhaar_card"  


from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)




# ================= PDF VIEW =================

def citizen_pdf(request, aadhaar):

    citizen = get_object_or_404(Citizen, aadhaar_card=aadhaar)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="Citizen_{aadhaar}.pdf"'
    )

    # ================= DOCUMENT =================

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )

    elements = []

    styles = getSampleStyleSheet()

    # ================= HEADING =================

    heading_style = styles["Heading1"]
    heading_style.alignment = 1  # center

    elements.append(Paragraph("Personal Information Record", heading_style))
    elements.append(Spacer(1, 12))

    # ================= WRAP STYLE (IMPORTANT FIX) =================

    wrap_style = ParagraphStyle(
        name="WrapStyle",
        fontSize=10,
        leading=14,
        alignment=TA_LEFT,
        wordWrap="LTR",
    )

    label_style = ParagraphStyle(
        name="LabelStyle",
        parent=wrap_style,
        fontName="Helvetica-Bold",
    )

    # ================= DATA =================

    fields = [
        "aadhaar_card",
        "name",
        "relation_type",
        "relation_aadhaar",
        "ward",
        "gpu",
        "district",
        "coi",
        "voter_id",
        "bank_number",
        "contact_no",
        "qualification",
        "profession",
        "home_category",
        "professional_details",
        "land_details",
        "schemes_applied",
        "health_status",
    ]

    table_data = []

    for field in fields:
        label = field.replace("_", " ").title()
        value = getattr(citizen, field) or "-"

        table_data.append([
            Paragraph(label, label_style),
            Paragraph(str(value), wrap_style),
        ])

    # ================= TABLE =================

    table = Table(
        table_data,
        colWidths=[170, 330],   # ⭐ FIXED WIDTH = WRAPPING WORKS
        repeatRows=0,
    )

    table.setStyle(TableStyle([

        # background label column
        ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),

        # borders
        ("GRID", (0, 0), (-1, -1), 1, colors.black),

        # padding
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),

        # ⭐ IMPORTANT: keep text aligned when rows grow
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))

    elements.append(table)

    # ================= BUILD PDF =================

    doc.build(elements)

    return response

# this is get fam  view






def get_family(request, aadhaar):

    try:
        person = Citizen.objects.get(aadhaar_card=aadhaar)
    except Citizen.DoesNotExist:
        return JsonResponse({"error": "Citizen not found"}, status=404)

    # -----------------------------------
    # STEP 1 — Identify Family Head
    # -----------------------------------

    if person.relation_type == "HEAD":
        head = person
    else:
        head = Citizen.objects.filter(
            aadhaar_card=person.relation_aadhaar
        ).first() or person

    # -----------------------------------
    # STEP 2 — Collect Family Members
    # -----------------------------------

    family_members = (
        Citizen.objects.filter(relation_aadhaar=head.aadhaar_card)
        | Citizen.objects.filter(aadhaar_card=head.aadhaar_card)
    ).distinct()

    # -----------------------------------
    # STEP 3 — Categorize (FIXED)
    # -----------------------------------

    wives = []
    children = []
    members = []

    for m in family_members:

        data = {
            "name": m.name,
            "aadhaar": m.aadhaar_card,
            "relation_type": m.relation_type,
        }

        members.append(data)

        # ✅ Wife must belong to THIS head
        if (
            m.relation_type == "WO"
            and m.relation_aadhaar == head.aadhaar_card
        ):
            wives.append(data)

        # ✅ Child must belong to THIS head
        elif (
            m.relation_type in ["SO", "DO"]
            and m.relation_aadhaar == head.aadhaar_card
        ):
            children.append(data)

    # -----------------------------------
    # STEP 4 — Detect Parents (Upper Tree)
    # -----------------------------------

    father = None
    mother = None

    if head.relation_type != "HEAD" and head.relation_aadhaar:

        parent = Citizen.objects.filter(
            aadhaar_card=head.relation_aadhaar
        ).first()

        if parent:
            father = {
                "name": parent.name,
                "aadhaar": parent.aadhaar_card,
                "relation_type": parent.relation_type,
            }

            mother_obj = Citizen.objects.filter(
                relation_type="WO",
                relation_aadhaar=parent.aadhaar_card
            ).first()

            if mother_obj:
                mother = {
                    "name": mother_obj.name,
                    "aadhaar": mother_obj.aadhaar_card,
                    "relation_type": mother_obj.relation_type,
                }

    # -----------------------------------
    # STEP 5 — Response
    # -----------------------------------

    response = {
        "family_head": head.name,
        "total_members": family_members.count(),
        "children_count": len(children),
        "father": father,
        "mother": mother,
        "wives": wives,
        "children": children,
        "members": members,
    }

    return JsonResponse(response)



# Family pdf generator 
def family_pdf(request, aadhaar):

    # -----------------------------------
    # Get Family JSON from existing API
    # -----------------------------------
    family_response = get_family(request, aadhaar)

    if family_response.status_code != 200:
        return family_response

    data = json.loads(family_response.content)

    # -----------------------------------
    # Create PDF Buffer
    # -----------------------------------
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        alignment=1,
        spaceAfter=15,
    )

    section_style = ParagraphStyle(
        "SectionStyle",
        parent=styles["Heading2"],
        spaceBefore=10,
        spaceAfter=8,
    )

    normal = styles["Normal"]

    elements = []

    # -----------------------------------
    # TITLE
    # -----------------------------------
    elements.append(
        Paragraph("Family Information Report", title_style)
    )

    # -----------------------------------
    # BASIC INFO
    # -----------------------------------
    summary_data = [
        ["Family Head", data["family_head"]],
        ["Total Members", data["total_members"]],
        ["Children Count", data["children_count"]],
    ]

    summary_table = Table(summary_data, colWidths=[150, 300])
    summary_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
        ("PADDING", (0,0), (-1,-1), 6),
    ]))

    elements.append(summary_table)
    elements.append(Spacer(1,12))

    # -----------------------------------
    # PARENTS
    # -----------------------------------
    elements.append(Paragraph("Parents", section_style))

    parent_data = [
        ["Relation", "Name", "Aadhaar"]
    ]

    if data["father"]:
        parent_data.append([
            "Father",
            data["father"]["name"],
            data["father"]["aadhaar"],
        ])

    if data["mother"]:
        parent_data.append([
            "Mother",
            data["mother"]["name"],
            data["mother"]["aadhaar"],
        ])

    if len(parent_data) == 1:
        parent_data.append(["-", "Not Available", "-"])

    parent_table = Table(parent_data, colWidths=[100, 200, 150])
    parent_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
    ]))

    elements.append(parent_table)

    # -----------------------------------
    # WIVES
    # -----------------------------------
    elements.append(Paragraph("Wives", section_style))

    wives_data = [["Name", "Aadhaar"]]

    for w in data["wives"]:
        wives_data.append([w["name"], w["aadhaar"]])

    if len(wives_data) == 1:
        wives_data.append(["-", "-"])

    wives_table = Table(wives_data, colWidths=[250, 200])
    wives_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
    ]))

    elements.append(wives_table)

    # -----------------------------------
    # CHILDREN
    # -----------------------------------
    elements.append(Paragraph("Children", section_style))

    children_data = [["Name", "Aadhaar", "Relation"]]

    for c in data["children"]:
        children_data.append([
            c["name"],
            c["aadhaar"],
            c["relation_type"],
        ])

    if len(children_data) == 1:
        children_data.append(["-", "-", "-"])

    children_table = Table(children_data, colWidths=[200, 150, 100])
    children_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
    ]))

    elements.append(children_table)

    # -----------------------------------
    # ALL MEMBERS
    # -----------------------------------
    elements.append(Paragraph("All Family Members", section_style))

    members_data = [["Name", "Aadhaar", "Relation"]]

    for m in data["members"]:
        members_data.append([
            m["name"],
            m["aadhaar"],
            m["relation_type"],
        ])

    members_table = Table(members_data, colWidths=[200, 150, 100])
    members_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
    ]))

    elements.append(members_table)

    # -----------------------------------
    # BUILD PDF
    # -----------------------------------
    doc.build(elements)

    buffer.seek(0)

    return HttpResponse(
        buffer,
        content_type="application/pdf",
        headers={
            "Content-Disposition":
            f'attachment; filename="Family_{aadhaar}.pdf"'
        },
    )