import click

from model import User, Role, RoleType
from session import SessionLocal
import auth


@click.group()
def cli():
    pass

@cli.command()
@click.argument("user_name", type=str)
@click.option("-r", "--role", required=True, type=click.Choice([e.name for e in RoleType]))
@click.option("-p", "--password", type=str, prompt=True, confirmation_prompt=True)
@click.option("-a", "--age", default=0, type=int)
def create_user(user_name, age, role, password):
    with SessionLocal() as session:
        # userの重複確認
        user = session.query(User).filter(User.username == user_name).first()
        if user:
            raise Exception(f"{user_name} is already exists.")

        # roleの存在確認
        role = session.query(Role).filter(Role.name == role).first()
        if role is None:
            raise Exception(f"{role} Role is not found.")

        user = User(
            username=user_name,
            hashed_password=auth.hash(password),
            age=age,
            roles=[role],
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

@cli.command()
@click.argument("user_name", type=str)
def delete_user(user_name):
    with SessionLocal() as session:
        # userの重複確認
        user = session.query(User).filter(User.username == user_name).first()
        if user is None:
            raise Exception(f"{user_name} is already exists.")
        session.delete(user)
        session.commit()

if __name__ == "__main__":
    cli()
