import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError

from apps.models import Category, Product


class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = "__all__"


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"


class Query(graphene.ObjectType):
    all_categories = graphene.List(CategoryType)
    all_products = graphene.List(ProductType)
    product = graphene.Field(ProductType, id=graphene.Int(required=True))

    def resolve_all_categories(self, info):
        return Category.objects.all()

    def resolve_all_products(self, info):
        return Product.objects.select_related("category").all()

    def resolve_product(self, info, id):
        try:
            return Product.objects.get(pk=id)
        except Product.DoesNotExist:
            raise GraphQLError("Product topilmadi")


class CreateProduct(graphene.Mutation):
    product = graphene.Field(ProductType)
    message = graphene.String()

    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String()
        price = graphene.Decimal(required=True)
        quantity = graphene.Int()
        category_id = graphene.Int(required=True)

    def mutate(self, info, title, price, category_id, description="", quantity=0):
        try:
            category = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            raise GraphQLError("Category topilmadi")

        product = Product.objects.create(
            title=title,
            description=description,
            price=price,
            quantity=quantity,
            category=category,
        )
        return CreateProduct(product=product, message="Product yaratildi")


class UpdateProduct(graphene.Mutation):
    product = graphene.Field(ProductType)
    message = graphene.String()

    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()
        description = graphene.String()
        price = graphene.Decimal()
        quantity = graphene.Int()
        category_id = graphene.Int()

    def mutate(self, info, id, title=None, description=None,
               price=None, quantity=None, category_id=None):
        try:
            product = Product.objects.get(pk=id)
        except Product.DoesNotExist:
            raise GraphQLError("Product topilmadi")

        if title is not None:
            product.title = title
        if description is not None:
            product.description = description
        if price is not None:
            product.price = price
        if quantity is not None:
            product.quantity = quantity
        if category_id is not None:
            try:
                product.category = Category.objects.get(pk=category_id)
            except Category.DoesNotExist:
                raise GraphQLError("Category topilmadi")

        product.save()
        return UpdateProduct(product=product, message="Product o'zgartirildi")


class DeleteProduct(graphene.Mutation):
    message = graphene.String()

    class Arguments:
        id = graphene.Int(required=True)

    def mutate(self, info, id):
        deleted, _ = Product.objects.filter(pk=id).delete()
        if not deleted:
            raise GraphQLError("Product topilmadi")
        return DeleteProduct(message="Product o'chirildi")


class Mutation(graphene.ObjectType):
    create_product = CreateProduct.Field()
    update_product = UpdateProduct.Field()
    delete_product = DeleteProduct.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
