from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from accounts.models import Profile
from audit.models import AuditLog
from contacts.models import ProjectContact
from documents.models import DocumentCategory, ProjectDocument
from equipment.models import ProjectEquipment, ProductionEquipment
from projects.models import City, Company, Project, ProjectStatus, ProjectTag
from software.models import Software, SoftwareUpdate


PASSWORD = "ProjectOffice2026!"


class Command(BaseCommand):
    help = "Создаёт демонстрационные данные для системы «Проектный офис»."

    def handle(self, *args, **options):
        users = self.create_users()
        cities = self.create_cities()
        statuses = self.create_statuses()
        companies = self.create_companies()
        tags = self.create_tags()
        software_items = self.create_software()
        categories = self.create_document_categories()

        projects = self.create_projects(
            users=users,
            cities=cities,
            statuses=statuses,
            companies=companies,
            tags=tags,
            software_items=software_items,
        )

        for index, project in enumerate(projects, start=1):
            self.create_contacts(project, companies, index)
            self.create_project_equipment(project, index)
            self.create_software_updates(project, users, index)
            self.create_documents(project, users["admin"], categories, index)
            self.create_history(project, users["admin"])

        self.create_production_equipment(projects)

        self.stdout.write(
            self.style.SUCCESS("Демонстрационные данные успешно созданы.")
        )

    def create_users(self):
        users_data = [
            {
                "username": "admin",
                "email": "admin@example.com",
                "full_name": "Полянский Герман Сергеевич",
                "role": Profile.Role.ADMIN,
                "is_superuser": True,
                "is_staff": True,
            },
            {
                "username": "pm_user",
                "email": "pm@example.com",
                "full_name": "Алексеев Михаил Игоревич",
                "role": Profile.Role.PROJECT_MANAGER,
                "is_superuser": False,
                "is_staff": False,
            },
            {
                "username": "pm_user_2",
                "email": "pm2@example.com",
                "full_name": "Васильева Марина Олеговна",
                "role": Profile.Role.PROJECT_MANAGER,
                "is_superuser": False,
                "is_staff": False,
            },
            {
                "username": "implementer_user",
                "email": "implementer@example.com",
                "full_name": "Орлова Екатерина Сергеевна",
                "role": Profile.Role.IMPLEMENTER,
                "is_superuser": False,
                "is_staff": False,
            },
            {
                "username": "implementer_user_2",
                "email": "implementer2@example.com",
                "full_name": "Соколов Артём Павлович",
                "role": Profile.Role.IMPLEMENTER,
                "is_superuser": False,
                "is_staff": False,
            },
            {
                "username": "engineer_user",
                "email": "engineer@example.com",
                "full_name": "Кузнецов Дмитрий Андреевич",
                "role": Profile.Role.ENGINEER,
                "is_superuser": False,
                "is_staff": False,
            },
            {
                "username": "guest_user",
                "email": "guest@example.com",
                "full_name": "Гость системы",
                "role": Profile.Role.GUEST,
                "is_superuser": False,
                "is_staff": False,
            },
        ]

        result = {}

        for item in users_data:
            user, created = User.objects.get_or_create(
                username=item["username"],
                defaults={
                    "email": item["email"],
                    "is_superuser": item["is_superuser"],
                    "is_staff": item["is_staff"],
                    "is_active": True,
                },
            )

            if created:
                user.set_password(PASSWORD)
                user.save()

            profile, _ = Profile.objects.get_or_create(user=user)
            profile.full_name = item["full_name"]
            profile.role = item["role"]
            profile.is_blocked = False
            profile.save()

            result[item["username"]] = user

        self.stdout.write("Пользователи: готово.")
        return result

    def create_cities(self):
        names = [
            "Пермь",
            "Москва",
            "Казань",
            "Екатеринбург",
            "Санкт-Петербург",
            "Новосибирск",
            "Тюмень",
            "Уфа",
            "Самара",
            "Нижний Новгород",
        ]

        result = []

        for name in names:
            city, _ = City.objects.get_or_create(name=name)
            result.append(city)

        self.stdout.write("Города: готово.")
        return result

    def create_statuses(self):
        data = [
            ("Новый", "#0d6efd"),
            ("В работе", "#ffc107"),
            ("Приостановлен", "#6c757d"),
            ("Завершён", "#198754"),
            ("Отменён", "#dc3545"),
        ]

        result = {}

        for name, color in data:
            status, _ = ProjectStatus.objects.get_or_create(
                name=name,
                defaults={"color": color},
            )
            result[name] = status

        self.stdout.write("Статусы: готово.")
        return result

    def create_companies(self):
        data = [
            ("ООО «ТРАФФИКДЭЙТА»", Company.CompanyType.OTHER),
            ("Администрация города Перми", Company.CompanyType.FINAL_CUSTOMER),
            ("Администрация города Казани", Company.CompanyType.FINAL_CUSTOMER),
            ("Администрация города Екатеринбурга", Company.CompanyType.FINAL_CUSTOMER),
            ("Департамент транспорта Москвы", Company.CompanyType.FINAL_CUSTOMER),
            ("Городской центр организации дорожного движения", Company.CompanyType.CUSTOMER if hasattr(Company.CompanyType, "CUSTOMER") else Company.CompanyType.OTHER),
            ("Тестовый заказчик", Company.CompanyType.CONTRACT_CUSTOMER),
            ("ООО «Инфраструктурные решения»", Company.CompanyType.CONTRACT_CUSTOMER),
            ("АО «Городские технологии»", Company.CompanyType.CONTRACT_CUSTOMER),
            ("Тестовый партнёр", Company.CompanyType.PARTNER),
        ]

        result = []

        for name, company_type in data:
            company, _ = Company.objects.get_or_create(
                name=name,
                defaults={"company_type": company_type},
            )
            result.append(company)

        self.stdout.write("Компании: готово.")
        return result

    def create_tags(self):
        names = [
            "Внедрение",
            "Пилот",
            "Городская инфраструктура",
            "Транспортная аналитика",
            "Видеоаналитика",
            "Тестовый проект",
            "Модернизация",
            "Производство",
            "Документооборот",
        ]

        result = []

        for name in names:
            tag, _ = ProjectTag.objects.get_or_create(name=name)
            result.append(tag)

        self.stdout.write("Теги: готово.")
        return result

    def create_software(self):
        data = [
            (
                "TrafficData Platform",
                "Платформа для управления проектами и транспортными данными.",
            ),
            (
                "Detector Control System",
                "Программное обеспечение для настройки и контроля детекторов.",
            ),
            (
                "Traffic Analytics Dashboard",
                "Панель аналитики транспортных потоков и загруженности дорог.",
            ),
        ]

        result = []

        for name, description in data:
            software, _ = Software.objects.get_or_create(
                name=name,
                defaults={"description": description},
            )
            result.append(software)

        self.stdout.write("ПО: готово.")
        return result

    def create_document_categories(self):
        names = [
            "Коммерческое предложение",
            "Техническое задание",
            "Договор с заказчиком",
            "Спецификация",
            "ПМИ",
            "Протокол сдачи проекта",
            "Закрывающие документы",
            "Счета на оплату",
            "Договорно-коммерческая документация",
            "Эксплуатационная документация",
            "Иные документы",
        ]

        result = {}

        for name in names:
            category, _ = DocumentCategory.objects.get_or_create(name=name)
            result[name] = category

        self.stdout.write("Категории документов: готово.")
        return result

    def create_projects(self, users, cities, statuses, companies, tags, software_items):
        project_titles = [
            "Внедрение системы транспортной видеоаналитики на перекрёстках города Перми",
            "Пилотный проект мониторинга транспортных потоков в Казани",
            "Модернизация оборудования дорожной аналитики в Екатеринбурге",
            "Создание единого реестра проектной документации",
            "Внедрение детекторов транспортного потока на магистралях Москвы",
            "Автоматизация учёта оборудования проектного офиса",
            "Подключение камер к системе транспортной аналитики",
            "Разработка контура хранения эксплуатационной документации",
            "Пилотная зона видеоаналитики в Новосибирске",
            "Интеграция серверов обработки данных в проектный контур",
            "Ведение проектов по модернизации городской инфраструктуры",
            "Создание карточек проектов для отдела внедрения",
            "Учёт программного обеспечения и версий в проектах",
            "Поставка оборудования для транспортных детекторов",
            "Подготовка проекта внедрения аналитической панели",
            "Тестирование процессов загрузки и скачивания документов",
            "Настройка ролей пользователей проектного офиса",
            "Расширение пилотной зоны транспортной видеоаналитики",
            "Проектирование базы данных для управления проектами",
            "Финальная демонстрация АИС «Проектный офис»",
        ]

        status_cycle = [
            statuses["В работе"],
            statuses["Новый"],
            statuses["Завершён"],
            statuses["Приостановлен"],
        ]

        projects = []

        for index, title in enumerate(project_titles, start=1):
            city = cities[(index - 1) % len(cities)]
            status = status_cycle[(index - 1) % len(status_cycle)]
            software = software_items[(index - 1) % len(software_items)]

            final_customer = companies[(index + 1) % len(companies)]
            contract_customer = companies[(index + 3) % len(companies)]

            manager = users["pm_user"] if index % 2 else users["pm_user_2"]
            implementer = users["implementer_user"] if index % 2 else users["implementer_user_2"]

            start_date = date(2026, 2, 1) + timedelta(days=index * 7)
            end_date = start_date + timedelta(days=45 + index)
            delivery_date = start_date + timedelta(days=30)

            project, created = Project.objects.get_or_create(
                title=title,
                defaults={
                    "city": city,
                    "final_customer": final_customer,
                    "contract_customer": contract_customer,
                    "manager": manager,
                    "implementer": implementer,
                    "status": status,
                    "start_date": start_date,
                    "end_date": end_date,
                    "delivery_date": delivery_date,
                    "software": software,
                    "active_software_version": f"1.{index % 5}.{index % 3}",
                    "budget": Decimal(900000 + index * 125000),
                    "password_manager_link": f"https://example.com/passwords/project-{index}",
                    "goal": (
                        "Обеспечить централизованное ведение информации по проекту, "
                        "оборудованию, документации, программному обеспечению и ответственным лицам."
                    ),
                    "situation_description": (
                        "Информация по проектам ранее велась в разрозненных файлах и таблицах. "
                        "Это затрудняло контроль сроков, актуальности данных и состава оборудования."
                    ),
                    "boundaries": (
                        "В рамках проекта учитываются карточка проекта, контакты, оборудование, "
                        "ПО, документы и история действий пользователей."
                    ),
                    "limitations": (
                        "Проект выполняется в учебном контуре. Интеграция с внешними системами "
                        "и промышленная эксплуатация не выполняются."
                    ),
                    "key_metrics": (
                        "Наличие заполненной карточки проекта.\n"
                        "Наличие контактных лиц.\n"
                        "Наличие оборудования и документов.\n"
                        "Фиксация действий в истории изменений."
                    ),
                },
            )

            selected_tags = [
                tags[(index - 1) % len(tags)],
                tags[index % len(tags)],
                tags[(index + 2) % len(tags)],
            ]
            project.tags.set(selected_tags)

            projects.append(project)

        self.stdout.write("Проекты: готово.")
        return projects

    def create_contacts(self, project, companies, index):
        contacts = [
            {
                "full_name": f"Иванов Сергей Петрович {index}",
                "position": "Представитель заказчика",
                "company": companies[index % len(companies)],
                "phone": f"+7 (342) 250-{index:02d}-10",
                "email": f"customer{index}@example.com",
                "notes": "Основной контакт по организационным вопросам проекта.",
            },
            {
                "full_name": f"Смирнова Анна Викторовна {index}",
                "position": "Специалист по документации",
                "company": companies[(index + 1) % len(companies)],
                "phone": f"+7 (342) 250-{index:02d}-20",
                "email": f"docs{index}@example.com",
                "notes": "Отвечает за договорные и проектные документы.",
            },
            {
                "full_name": f"Кузнецов Дмитрий Андреевич {index}",
                "position": "Технический специалист",
                "company": companies[0],
                "phone": f"+7 (342) 250-{index:02d}-30",
                "email": f"tech{index}@example.com",
                "notes": "Участвует в настройке оборудования и проверке работоспособности.",
            },
        ]

        for item in contacts:
            ProjectContact.objects.get_or_create(
                project=project,
                full_name=item["full_name"],
                defaults=item,
            )

    def create_project_equipment(self, project, index):
        items = [
            {
                "equipment_type": ProjectEquipment.EquipmentType.DETECTOR,
                "name": f"Детектор транспортного потока TD-{index:02d}",
                "quantity": 2 + index % 5,
                "cameras_per_detector": 2 + index % 3,
                "description": "Используется для обработки видеопотока с камер на перекрёстках.",
            },
            {
                "equipment_type": ProjectEquipment.EquipmentType.SERVER,
                "name": f"Сервер обработки данных SRV-{index:02d}",
                "quantity": 1,
                "cameras_per_detector": None,
                "description": "Сервер предназначен для обработки и хранения данных проекта.",
            },
        ]

        for item in items:
            ProjectEquipment.objects.get_or_create(
                project=project,
                name=item["name"],
                defaults=item,
            )

    def create_software_updates(self, project, users, index):
        responsible = users["implementer_user"] if index % 2 else users["implementer_user_2"]

        versions = [
            f"1.{index % 5}.0",
            f"1.{index % 5}.1",
        ]

        for number, version in enumerate(versions, start=1):
            SoftwareUpdate.objects.get_or_create(
                project=project,
                version=version,
                defaults={
                    "update_date": project.start_date + timedelta(days=number * 10),
                    "responsible": responsible,
                    "changes_description": (
                        f"Обновление версии {version}: добавлены настройки проекта, "
                        "уточнены данные по оборудованию и документации."
                    ),
                    "update_reason": "Плановое обновление в рамках реализации проекта.",
                },
            )

    def create_documents(self, project, admin, categories, index):
        documents = [
            {
                "category": categories["Техническое задание"],
                "filename": f"tz_project_{index:02d}.txt",
                "comment": "Тестовый файл технического задания.",
                "content": (
                    f"Техническое задание по проекту: {project.title}\n\n"
                    "Цель: описание требований к проекту, оборудованию, ПО и документации."
                ),
            },
            {
                "category": categories["Коммерческое предложение"],
                "filename": f"kp_project_{index:02d}.txt",
                "comment": "Коммерческое предложение по проекту.",
                "content": (
                    f"Коммерческое предложение по проекту: {project.title}\n\n"
                    f"Ориентировочный бюджет проекта: {project.budget} рублей."
                ),
            },
            {
                "category": categories["ПМИ"],
                "filename": f"pmi_project_{index:02d}.txt",
                "comment": "Программа и методика испытаний.",
                "content": (
                    "Проверяются сценарии: авторизация, просмотр проекта, "
                    "добавление данных, загрузка документов и история изменений."
                ),
            },
        ]

        for item in documents:
            exists = ProjectDocument.objects.filter(
                project=project,
                original_name=item["filename"],
            ).exists()

            if exists:
                continue

            document = ProjectDocument(
                project=project,
                category=item["category"],
                uploaded_by=admin,
                original_name=item["filename"],
                comment=item["comment"],
            )

            document.file.save(
                item["filename"],
                ContentFile(item["content"].encode("utf-8")),
                save=True,
            )

    def create_history(self, project, admin):
        records = [
            ("Создан проект", "Создан демонстрационный проект."),
            ("Добавлены контакты", "Добавлены контактные лица проекта."),
            ("Добавлено оборудование", "Добавлено проектное оборудование."),
            ("Загружены документы", "Загружены тестовые документы проекта."),
            ("Добавлены обновления ПО", "Добавлены записи истории обновлений программного обеспечения."),
        ]

        for action, description in records:
            AuditLog.objects.get_or_create(
                project=project,
                user=admin,
                action=action,
                description=description,
                defaults={
                    "model_name": "DemoData",
                    "object_id": project.id,
                },
            )

    def create_production_equipment(self, projects):
        items = []

        for index in range(1, 31):
            if index % 4 == 1:
                production_type = ProductionEquipment.ProductionType.CAMERA
                name = f"Камера Hikvision DS-2CD-{index:02d}"
            elif index % 4 == 2:
                production_type = ProductionEquipment.ProductionType.BOARD
                name = f"Плата детектора TD-BOARD-{index:02d}"
            elif index % 4 == 3:
                production_type = ProductionEquipment.ProductionType.SWITCH
                name = f"Коммутатор TP-Link TL-SG-{index:02d}"
            else:
                production_type = ProductionEquipment.ProductionType.POWER_SUPPLY
                name = f"Блок питания Mean Well 12V-{index:02d}"

            if index <= 14:
                status = ProductionEquipment.Status.ATTACHED
                project = projects[(index - 1) % len(projects)]
            elif index <= 22:
                status = ProductionEquipment.Status.FREE
                project = None
            elif index <= 26:
                status = ProductionEquipment.Status.RESERVED
                project = None
            else:
                status = ProductionEquipment.Status.ORDERED
                project = None

            items.append(
                {
                    "production_type": production_type,
                    "name": name,
                    "quantity": 1 + index % 8,
                    "status": status,
                    "project": project,
                }
            )

        for item in items:
            ProductionEquipment.objects.get_or_create(
                name=item["name"],
                defaults=item,
            )

        self.stdout.write("Производственное оборудование: готово.")