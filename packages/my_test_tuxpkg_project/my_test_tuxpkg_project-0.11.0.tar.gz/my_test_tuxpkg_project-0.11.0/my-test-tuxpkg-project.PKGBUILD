pkgname=my-test-tuxpkg-project
pkgver=0.11.0
pkgrel=1
pkgdesc='FIXME'
url='FIXME'
license=('FIXME')
arch=('any')
depends=('python' 'python-jinja')
makedepends=('git' 'python-build' 'python-flit' 'python-installer' 'python-wheel')
checkdepends=('python-pytest' 'python-pytest-mock')
source=("$pkgname-$pkgver.tar.gz")
sha256sums=('SKIP')

build() {
  cd "$pkgname-$pkgver"
  python -m build --wheel --no-isolation
}

check() {
  cd "$pkgname-$pkgver"
  PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest
}

package() {
  cd "$pkgname-$pkgver"
  python -m installer --destdir="$pkgdir" dist/*.whl
  install -Dvm644 LICENSE -t "$pkgdir/usr/share/licenses/$pkgname"
}
