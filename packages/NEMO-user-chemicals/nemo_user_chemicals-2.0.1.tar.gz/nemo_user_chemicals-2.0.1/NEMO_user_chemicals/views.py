from datetime import timedelta

from NEMO.models import Chemical, ChemicalHazard, User
from NEMO.utilities import EmailCategory, render_email_template, send_mail
from NEMO.views.customization import get_media_file_contents
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from NEMO_user_chemicals.customizations import ChemicalsCustomization
from NEMO_user_chemicals.forms import ChemicalForm, ChemicalRequestApprovalForm, ChemicalRequestForm, UserChemicalForm
from NEMO_user_chemicals.models import ChemicalLocation, ChemicalRequest, UserChemical


@login_required
@require_http_methods(["GET", "POST"])
def chemical_request(request):
    hazards = ChemicalHazard.objects.all()
    dictionary = {"hazards": hazards}
    if request.method == "POST":
        form = ChemicalRequestForm(request.user, data=request.POST, files=request.FILES)
        if form.is_valid():
            req = form.save()
            send_new_chemical_request_email(req)
            dictionary = {
                "title": "Request received",
                "heading": "Your request has been received and will be evaluated by the staff",
            }
        else:
            dictionary = {
                "title": "Chemical request failed",
                "heading": "Invalid form data",
                "content": str(form.errors),
            }
        return render(request, "acknowledgement.html", dictionary)
    return render(request, "NEMO_user_chemicals/chemical_request.html", dictionary)


@staff_member_required(login_url=None)
@require_GET
def view_requests(request, sort_by=""):
    dictionary = {}
    all_requests = ChemicalRequest.objects.all()
    dictionary = {}
    if sort_by in ["requester", "name", "approved"]:
        all_requests = all_requests.order_by(sort_by)
    else:
        all_requests = all_requests.order_by("-date")
    dictionary["all_requests"] = all_requests
    pending_requests = all_requests.filter(approved=0)
    dictionary["pending_requests"] = pending_requests
    return render(request, "NEMO_user_chemicals/view_requests.html", dictionary)


@staff_member_required(login_url=None)
@require_http_methods(["GET", "POST"])
def request_details(request, request_id):
    chem_req = get_object_or_404(ChemicalRequest, id=request_id)
    hazards = [h for h in chem_req.hazards.all()]
    dictionary = {"chemical_request": chem_req, "hazards": hazards}
    return render(request, "NEMO_user_chemicals/request_details.html", dictionary)


def send_new_chemical_request_email(chemical_request):
    message = get_media_file_contents("chemical_request_email.html")
    if message:
        chem_request_emails = ChemicalsCustomization.get("chemical_request_email_addresses")
        requester = chemical_request.requester.get_full_name()
        subject = f"New Material Request from {requester}"
        content = render_email_template(message, {"chemical_request": chemical_request})
        recipients = tuple([e for e in chem_request_emails.split(",") if e])
        send_mail(
            subject=subject,
            content=content,
            to=recipients,
            from_email=chemical_request.requester.email,
            email_category=EmailCategory.SAFETY,
        )


@staff_member_required(login_url=None)
@require_http_methods(["GET", "POST"])
def update_request(request, request_id):
    chemical_request = get_object_or_404(ChemicalRequest, id=request_id)
    form = ChemicalRequestApprovalForm(request.user, data=request.POST, instance=chemical_request)
    if not form.is_valid():
        dictionary = {
            "title": "Chemical request update failed",
            "heading": "Invalid form data",
            "content": str(form.errors),
        }
        return render(request, "acknowledgement.html", dictionary)
    chem_req = form.save()
    send_chemical_request_email_update(chem_req)
    return redirect("view_requests")


def send_chemical_request_email_update(chemical_request):
    message = get_media_file_contents("chemical_request_update_email.html")
    if message:
        subject = f"Update to your Material Request for {chemical_request.name}"
        message = render_email_template(message, {"chemical_request": chemical_request})
        chem_request_emails = ChemicalsCustomization.get("chemical_request_email_addresses")
        recipients = tuple([e for e in chem_request_emails.split(",") if e])
        send_mail(
            subject=subject,
            content=message,
            from_email=chemical_request.approver.email,
            to=[chemical_request.requester.email],
            cc=recipients,
            email_category=EmailCategory.SAFETY,
        )


@staff_member_required(login_url=None)
@require_GET
def user_chemicals(request, sort_by=""):
    dictionary = {}
    user_chemicals = UserChemical.objects.all()
    if sort_by in ["owner", "chemical", "in_date", "expiration", "location", "label_id"]:
        user_chemicals = user_chemicals.order_by(sort_by)
    else:
        user_chemicals = user_chemicals.order_by("location")
    dictionary["user_chemicals"] = user_chemicals
    return render(request, "NEMO_user_chemicals/user_chemicals.html", dictionary)


@staff_member_required(login_url=None)
@require_http_methods(["GET", "POST"])
def add_user_chemical(request, chem_req=None):
    if request.method == "GET":
        chem_request = get_object_or_404(ChemicalRequest, id=chem_req) if chem_req else None
        dictionary = {
            "one_year_from_now": timezone.now() + timedelta(days=365),
            "today": timezone.now().date(),
            "users": User.objects.filter(is_active=True),
            "chemicals": Chemical.objects.all(),
            "chemical_request": chem_request,
            "locations": ChemicalLocation.objects.all(),
        }
        return render(request, "NEMO_user_chemicals/add_user_chemical.html", dictionary)
    elif request.method == "POST":
        form = UserChemicalForm(data=request.POST)
        if form.is_valid() and not form.cleaned_data.get("chemical"):
            form.add_error("chemical", "You must select a valid chemical from the list.")
        if not form.is_valid():
            dictionary = {
                "title": "Chemical request failed",
                "heading": "Invalid form data",
                "content": str(form.errors),
            }
            return render(request, "acknowledgement.html", dictionary)
        user_chem = form.save(commit=False)
        comments = form.cleaned_data.get("comments") or request.POST.get("comments", "")
        timestamp = timezone.now().strftime("%Y-%m-%d %H:%M")
        history_entry = f"[{timestamp}] Added: Owner: {user_chem.owner.get_full_name()}, Label ID: {user_chem.label_id}, Date In: {user_chem.in_date}, Expiration: {user_chem.expiration}. Comments: {comments}\n"
        user_chem.history = (user_chem.history or "") + history_entry
        user_chem.save()
        return HttpResponseRedirect(reverse("user_chemicals"))


@staff_member_required(login_url=None)
@require_http_methods(["GET", "POST"])
def update_user_chemical(request, chem_id):
    user_chem = get_object_or_404(UserChemical, id=chem_id)
    if request.method == "GET":
        form = UserChemicalForm(instance=user_chem)
        owner = user_chem.owner
        dictionary = {
            "form": form,
            "one_year_from_now": timezone.now() + timedelta(days=365),
            "users": User.objects.filter(is_active=True),
            "owner": owner,
            "chemicals": Chemical.objects.all(),
            "locations": ChemicalLocation.objects.all(),
        }
        return render(request, "NEMO_user_chemicals/update_user_chemical.html", dictionary)
    elif request.method == "POST":
        user_chem = get_object_or_404(UserChemical, id=chem_id)
        form = UserChemicalForm(data=request.POST, instance=user_chem)
        if form.is_valid() and not form.cleaned_data.get("chemical"):
            form.add_error("chemical", "You must select a valid chemical from the list.")
        if not form.is_valid():
            dictionary = {
                "title": "Chemical request update failed",
                "heading": "Invalid form data",
                "content": str(form.errors),
            }
            return render(request, "acknowledgement.html", dictionary)
        user_chem = form.save(commit=False)
        comments = form.cleaned_data.get("comments") or request.POST.get("comments", "")
        timestamp = timezone.now().strftime("%Y-%m-%d %H:%M")
        history_entry = f"[{timestamp}] Updated: Owner: {user_chem.owner.get_full_name()}, Label ID: {user_chem.label_id}, Date In: {user_chem.in_date}, Expiration: {user_chem.expiration}. Comments: {comments}\n"
        user_chem.history = (user_chem.history or "") + history_entry
        user_chem.save()
        return HttpResponseRedirect(reverse("user_chemicals"))


@staff_member_required(login_url=None)
@require_POST
def delete_user_chemical(request, chem_id):
    try:
        user_chem = UserChemical.objects.get(id=chem_id)
        user_chem.delete()
    except UserChemical.DoesNotExist:
        pass
    return redirect(reverse("user_chemicals"))


@staff_member_required(login_url=None)
@require_http_methods(["GET", "POST"])
def add_chemical(request, request_id=None):
    chem_req = None
    if request_id:
        chem_req = get_object_or_404(ChemicalRequest, id=request_id)

    if request.method == "POST":
        form = ChemicalForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            chemical = form.save(commit=False)
            # If no document uploaded but we have a request with an SDS, copy it
            if not chemical.document and chem_req and chem_req.sds:
                chemical.document.save(chem_req.sds.name, chem_req.sds)
            chemical.save()
            form.save_m2m()
            return redirect("view_requests")
    else:
        initial_data = {}
        if chem_req:
            initial_data["name"] = chem_req.name
            initial_data["hazards"] = chem_req.hazards.values_list("id", flat=True)

        form = ChemicalForm(initial=initial_data)

    return render(request, "NEMO_user_chemicals/add_chemical.html", {"form": form, "source_request": chem_req})
